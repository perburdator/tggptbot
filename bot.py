
import telebot

from telebot import types

from other import *

from gpt import GPT

from sql3lite import *

# Создание скелета нейросети
gpt = GPT(system_content="Ты дружелюбный помощник по математике и физике.")
# Создание
token = mytoken
bot = telebot.TeleBot(token=token)

# логирование для соответствия ТЗ было бы хорошо вынести из этого файла но мне лень)))
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
    user_id = message.from_user.id
    bot.send_sticker(user_id,
                     "CAACAgIAAxkBAAEDqttl1tZVKZFp4PO5YtGJN8XVwcj9SwAC2A8AAkjyYEsV-8TaeHRrmDQE")  # добавил стикер для приветствования
    bot.send_message(user_id, text_start)

# функция дебаг для меня
@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)
    with open("log_file_sqlite3.txt", "rb") as file:
        bot.send_document(message.chat.id, file)

@bot.message_handler(commands=["how_to"])
def how_to_func(message):
    user_id = message.from_user.id
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = types.KeyboardButton(text='математика')
    button2 = types.KeyboardButton(text='физика')
    keyboard.add(button1, button2)
    logging.info('Sending HowTo text')
    bot.send_message(user_id, text=text_how_to, reply_markup=keyboard)
    bot.send_message(user_id, 'Чем могу помочь?')
    bot.register_next_step_handler(message, solve_task)


# обработка действий состояния "Обращение к GPT для решения новой задачи"
@bot.message_handler(content_types=['text'])
def solve_task(message):
    user_id = message.from_user.id
    if message.text == 'математика' or message.text == 'физика':
        add_user(db_file, user_id, subject=message.text, level="", answer="")
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button1 = types.KeyboardButton(text='advanced')
        button2 = types.KeyboardButton(text='beginner')
        keyboard.add(button1, button2)
        bot.send_message(user_id, text="Выберите уровень *сложности* ответа от нейросети", reply_markup=keyboard)
        bot.register_next_step_handler(message, get_level)
    else:
        bot.send_message(user_id, text=text_for_error)
        bot.register_next_step_handler(message, how_to_func)
def get_level(message):
    user_id = message.from_user.id
    if message.text == 'advanced' or message.text == 'beginner':
        update_user_level(db_file, level=message.text, user_id=user_id)
        bot.send_message(user_id, 'Теперь можете задать вопрос: ')
        bot.register_next_step_handler(message, get_promt)
    else:
        bot.send_message(user_id, text=text_for_error)
        bot.register_next_step_handler(message, solve_task)

# обработка действий для состояния "Получение ответа"
def get_promt(message):
    user_id = message.from_user.id
    user_request = message.text
    user_level = get_user_level(db_file, user_id=user_id)
    logging.debug(f"Text from user: {message.text}")
    request_tokens = gpt.count_tokens(user_request)
    while request_tokens > gpt.MAX_TOKENS:
        user_request = bot.send_message(user_id, "Запрос несоответствует кол-ву токенов\nИсправьте запрос: ")
        request_tokens = gpt.count_tokens(user_request)

    if user_level[0] == 'beginner':
        # Создание промта
        json = gpt.make_promt(user_request, system_content=system_content_text_beginner)

        # Запрос
        resp = gpt.send_request(json)

        # Проверяем ответ на наличие ошибок и делаем в читабельный вид.
        response = gpt.process_resp(resp)
        if not response[0]:
            bot.send_message(user_id, "Не удалось выполнить запрос")  # ошибка
            logging.error('Cant get response from AI')
        add_answer(db_file=db_file, user_id=user_id, answer=response[1])
        # Выводим ответ
        bot.send_message(user_id, response[1])
        logging.info('Success! send response to user')

    if user_level[0] == 'advanced':
        # Создание промта
        json = gpt.make_promt(user_request, system_content=system_content_text_advanced)

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
    button2 = types.KeyboardButton(text='достаточно')
    keyboard.add(button1, button2)
    bot.send_message(user_id, text="Продолжить ответ?", reply_markup=keyboard)
    logging.info('Waiting choice from user')
    bot.register_next_step_handler(message, continue_filter)

def continue_filter(message):
    user_id = message.from_user.id
    if message.text == 'достаточно':
        gpt.clear_history()
        delete_user(db_file, user_id)
        bot.send_message(user_id, 'Хорошо, нажмите /start')
    elif message.text == 'продолжи':
        answer_get = get_user_answer(db_file, user_id)
        gpt.make_promt((answer_get+'продолжи'), system_content_text_continuation)
        bot.send_message(user_id, "Ожидайте ответ")


if __name__ == "__main__":
    logging.info("Bot is now running")
    db_file = "user_of_bot.db"
    bot.infinity_polling()
