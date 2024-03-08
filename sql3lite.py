import logging
import sqlite3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file_sqlite3.txt",
    filemode="w",
)

def execute_query(db_file, query, data=None):
    try:
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

        connection.commit()

        return cursor

    except sqlite3.Error as e:
        logging.error("Error of connection", e)

    finally:
        connection.close()

def get_user_level(db_file, user_id):
    query = """
        SELECT level
        FROM users
        WHERE user_id = ?;
    """
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results[0] if results else None

    logging.debug("Got user level for answer")

def get_user_answer(db_file, user_id):
    query = """
        SELECT answer
        FROM users
        WHERE user_id = ?;
    """
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results[0] if results else None

    logging.debug("Got answer from AI")

def add_user(db_file, user_id, subject, level, answer):
    query = """
        INSERT INTO users (user_id, subject, level, answer)
        VALUES (?, ?, ?, ?)
    """
    data = (user_id, subject, level, answer)

    execute_query(db_file, query, data)
    logging.info("New user successfully added")

def add_answer(db_file, user_id, answer):
    query = """
        INSERT INTO users (user_id, answer)
        VALUES (?, ?)
    """
    data = (user_id, answer)

    execute_query(db_file, query, data)
    logging.info("New user successfully added")
def update_user_level(db_file, user_id, level):
    query = """
        UPDATE users
        SET level = ?
        WHERE user_id = ?
    """
    data = (level, user_id)

    execute_query(db_file, query, data)
    logging.info("Info successfully updated")


def delete_user(db_file, user_id):
    query = """
        DELETE  
        FROM users
        WHERE user_id = ?
    """
    data = (user_id,)

    execute_query(db_file, query, data)
    logging.info("Successfully deleted userdata")


if __name__ == "__main__":
    db_file = 'user_of_bot.db'

    # add_user(db_file, '199912331', 'math')

    # update_user_level(db_file, '199912331', 'beginner')
    # update_user_level(db_file, '199912331', 'advanced')
    # delete_user(db_file, 1983380542)  отладочные команды
