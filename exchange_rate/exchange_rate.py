import requests
import logging

def get_currency():
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        return response['Valute']
    except Exception as e:
        logging.error(f'{e.__class__}, {e}', exc_info=True)
        return None


if __name__ == '__main__':
    print(get_currency())
