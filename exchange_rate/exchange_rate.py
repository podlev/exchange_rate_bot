import requests


def get_currency():
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        return response['Valute']
    except Exception as e:
        print(e)
        return {}


if __name__ == '__main__':
    print(get_currency())
