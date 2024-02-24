
import telebot

import logging

from telebot import types

from other import mytoken, text_how_to, text_start

from gpt import GPT
# Создание скелета нейросети
gpt = GPT(system_content="Ты - дружелюбный помощник для решения  разных задач. Давай краткий ответ на русском языке")
# Создание
token = mytoken
bot = telebot.TeleBot(token=token)

# логирование для соответствия ТЗ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

@bot.message_handler(commands=['about'])
def send_about(message):
    with open("README.md", "rb") as f:
        logging.info('Sending doc to user')
        bot.send_document(message.chat.id, f)

@bot.message_handler(commands=["start"])
def start_func(message):
    logging.info("Sending start text")
    user = message.from_user.id
    bot.send_sticker(user,
                     "CAACAgIAAxkBAAEDqttl1tZVKZFp4PO5YtGJN8XVwcj9SwAC2A8AAkjyYEsV-8TaeHRrmDQE")  # добавил стикер для приветствования
    bot.send_message(user, text_start)

# функция дебаг для меня
@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=["how_to"])
def how_to_func(message):
    user_id = message.from_user.id
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = types.KeyboardButton(text='задать вопрос')
    keyboard.add(button1)
    logging.info('Sending HowTo text')
    bot.send_message(user_id, text=text_how_to, reply_markup=keyboard)
    bot.register_next_step_handler(message, solve_task)


# обработка действий состояния "Обращение к GPT для решения новой задачи"
@bot.message_handler(content_types=['text'])
def solve_task(message):
    user_id = message.from_user.id
    if message.text == "задать вопрос":
        bot.send_message(user_id, text="Напишите свой вопрос: ")
        bot.register_next_step_handler(message, get_promt)

# обработка действий для состояния "Получение ответа"
def get_promt(message):

    user_id = message.from_user.id
    user_request = message.text
    logging.debug(f"Text from user: {message.text}")
    request_tokens = gpt.count_tokens(user_request)
    while request_tokens > gpt.MAX_TOKENS:
        user_request = bot.send_message(user_id, "Запрос несоответствует кол-ву токенов\nИсправьте запрос: ")
        request_tokens = gpt.count_tokens(user_request)

    # Не продолжаем, и удаляем историю у нейросетки.
    if user_request.lower() != 'продолжи':
        gpt.clear_history()
    # костыль для слова продолжи, тк он не реагировал на это слово в преписке.
    elif user_request.lower() == 'продолжи':
        bot.send_message(user_id, 'Хорошо, ожидайте ответ...')
        logging.info('User waiting')
        gpt.make_promt(user_request)
    # Создание промта
    json = gpt.make_promt(user_request)

    # Запрос
    resp = gpt.send_request(json)

    # Проверяем ответ на наличие ошибок и делаем в читабельный вид.
    response = gpt.process_resp(resp)
    if not response[0]:
        bot.send_message(user_id, "Не удалось выполнить запрос")  # ошибка
        logging.error('Cant get response from AI')
    # Выводим ответ
    bot.send_message(user_id, response[1])
    logging.info('Success! send response to user')
    # Создаем клавиатуру для соответсвия ТЗ
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = types.KeyboardButton(text='продолжи')
    keyboard.add(button1)
    bot.send_message(user_id, text="Продолжить ответ? Если нет, то просто пришлите новый запрос", reply_markup=keyboard)
    logging.info('Waiting choice from user')
    bot.register_next_step_handler(message, get_promt)


if __name__ == "__main__":
    logging.info("Bot is now running")
    bot.infinity_polling()
