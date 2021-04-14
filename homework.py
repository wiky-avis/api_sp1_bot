import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram

from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    filename='my_logger.log',
    maxBytes=50000000,
    backupCount=5,
    encoding='utf-8')
logger_formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(name)s')
handler.setFormatter(logger_formatter)
logger.addHandler(handler)
logger.info('Настройка логгирования окончена!')


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework.get('status') == 'reviewing':
        verdict = 'Работа взята в ревью.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
        headers=headers, params=params)
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.debug('Бот запущен!')
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]), bot_client)
                logger.info('Сообщение отправлено!')
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)
            time.sleep(1200)

        except Exception as error:
            logging.error(f'Бот столкнулся с ошибкой: {error}')
            send_message('Бот столкнулся с ошибкой', bot_client)
            time.sleep(300)


if __name__ == '__main__':
    main()
