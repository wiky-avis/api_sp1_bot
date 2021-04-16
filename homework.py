import json
import logging
import logging.config  # без этого импорта, код не работает
# AttributeError: module 'logging' has no attribute 'config'
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'fileHandler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'myFormatter',
            'filename': 'my_logger.log',
            'maxBytes': 50000000,
            'backupCount': 5,
            'encoding': 'utf-8'}},
    'loggers': {
        'info': {
            'handlers': ['fileHandler'],
            'level': 'INFO'},
        'debug': {
            'handlers': ['fileHandler'],
            'level': 'DEBUG'}},
    'formatters': {
        'myFormatter': {
            'format': '%(asctime)s, %(levelname)s, %(message)s'}}}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('info')
logger = logging.getLogger('debug')
logger.info('Настройка логгирования окончена!')

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if homework_name is None or status is None:
        return logger.error('Неверный ответ сервера')
    elif status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'reviewing':
        verdict = 'Работа взята в ревью.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    current_timestamp = (
        int(time.time()) if current_timestamp is None else current_timestamp)
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=params)
        homework_statuses.raise_for_status()
    except requests.exceptions.ConnectionError as error:
        logger.error(f'Проблема с сетью: {error}')
        return dict()
    except requests.exceptions.HTTPError as error:
        logger.error(f'Недопустимый HTTP-ответ: {error}')
        return dict()
    except requests.exceptions.Timeout as error:
        logger.error(f'Время ожидания запроса истекло: {error}')
        return dict()
    except requests.exceptions.TooManyRedirects as error:
        logger.error(f'Несуществующий URL: {error}')
        return dict()
    else:
        try:
            return homework_statuses.json()
        except json.JSONDecodeError as error:
            logger.error(f'Это не JSON: {error}')
            return dict()


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
            logger.error(f'Бот столкнулся с ошибкой: {error}')
            send_message('Бот столкнулся с ошибкой', bot_client)
            time.sleep(300)


if __name__ == '__main__':
    main()
