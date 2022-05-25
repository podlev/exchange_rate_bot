import asyncio
import logging
from datetime import datetime, timedelta
from pprint import pprint

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from exchange_rate.exchange_rate import get_currency
from database.db import engine, User, Subscribe, SubscribeType
from sqlalchemy.orm import Session

from os import getenv
from sys import exit

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

MAIN_BUTTONS = ('Получить курс валюты',
                'Выбрать валюту',
                'Настроить отслеживание',
                'Помощь')

RATE_BUTTONS = ('Отслеживание по времени',
                'Отслеживание при изменении',
                'Мои отслеживания',
                'Назад')

DELAY_BUTTONS = ('Раз в минуту',
                 'Раз в час',
                 'Раз в сутки',
                 'Не отслеживать по времени',
                 'Вернуться')

DELTA_BUTTONS = ('Изменение на 1 копейку',
                 'Изменение на 10 копеек',
                 'Изменение на 1 рубль',
                 'Не отслеживать изменение',
                 'Вернуться')

currency = {'AUD': {'Nominal': 1, 'Name': 'Австралийский доллар', 'Value': 40.0121, 'Previous': 40.3511},
            'AZN': {'Nominal': 1, 'Name': 'Азербайджанский манат', 'Value': 33.1174, 'Previous': 33.5112},
            'GBP': {'Nominal': 1, 'Name': 'Фунт стерлингов Соединенного королевства', 'Value': 70.5152,
                    'Previous': 71.6157},
            'AMD': {'Nominal': 100, 'Name': 'Армянских драмов', 'Value': 12.4913, 'Previous': 12.5843},
            'BYN': {'Nominal': 1, 'Name': 'Белорусский рубль', 'Value': 22.8981, 'Previous': 23.113},
            'BGN': {'Nominal': 1, 'Name': 'Болгарский лев', 'Value': 30.6827, 'Previous': 31.0475},
            'BRL': {'Nominal': 1, 'Name': 'Бразильский реал', 'Value': 11.704, 'Previous': 11.876},
            'HUF': {'Nominal': 100, 'Name': 'Венгерских форинтов', 'Value': 15.6019, 'Previous': 15.9136},
            'HKD': {'Nominal': 10, 'Name': 'Гонконгских долларов', 'Value': 71.8474, 'Previous': 72.7109},
            'DKK': {'Nominal': 10, 'Name': 'Датских крон', 'Value': 81.1081, 'Previous': 81.6034},
            'USD': {'Nominal': 1, 'Name': 'Доллар США', 'Value': 56.2996, 'Previous': 56.969},
            'EUR': {'Nominal': 1, 'Name': 'Евро', 'Value': 57.921, 'Previous': 58.8705},
            'INR': {'Nominal': 100, 'Name': 'Индийских рупий', 'Value': 72.5776, 'Previous': 73.3654},
            'KZT': {'Nominal': 100, 'Name': 'Казахстанских тенге', 'Value': 13.504, 'Previous': 13.4095},
            'CAD': {'Nominal': 1, 'Name': 'Канадский доллар', 'Value': 43.8949, 'Previous': 44.4064},
            'KGS': {'Nominal': 100, 'Name': 'Киргизских сомов', 'Value': 70.8171, 'Previous': 71.6591},
            'CNY': {'Nominal': 10, 'Name': 'Китайских юаней', 'Value': 85.902, 'Previous': 87.0648},
            'MDL': {'Nominal': 10, 'Name': 'Молдавских леев', 'Value': 29.4456, 'Previous': 29.7328},
            'NOK': {'Nominal': 10, 'Name': 'Норвежских крон', 'Value': 58.6582, 'Previous': 59.2304},
            'PLN': {'Nominal': 1, 'Name': 'Польский злотый', 'Value': 12.9848, 'Previous': 13.2625},
            'RON': {'Nominal': 1, 'Name': 'Румынский лей', 'Value': 12.1629, 'Previous': 12.339},
            'XDR': {'Nominal': 1, 'Name': 'СДР', 'Value': 75.9994, 'Previous': 76.8899},
            'SGD': {'Nominal': 1, 'Name': 'Сингапурский доллар', 'Value': 41.0168, 'Previous': 41.4531},
            'TJS': {'Nominal': 10, 'Name': 'Таджикских сомони', 'Value': 49.3856, 'Previous': 48.2788},
            'TRY': {'Nominal': 10, 'Name': 'Турецких лир', 'Value': 34.9709, 'Previous': 35.9115},
            'TMT': {'Nominal': 1, 'Name': 'Новый туркменский манат', 'Value': 16.0856, 'Previous': 16.2769},
            'UZS': {'Nominal': 10000, 'Name': 'Узбекских сумов', 'Value': 50.8352, 'Previous': 51.3933},
            'UAH': {'Nominal': 10, 'Name': 'Украинских гривен', 'Value': 19.0282, 'Previous': 19.3772},
            'CZK': {'Nominal': 10, 'Name': 'Чешских крон', 'Value': 24.4738, 'Previous': 24.6897},
            'SEK': {'Nominal': 10, 'Name': 'Шведских крон', 'Value': 57.2569, 'Previous': 58.3018},
            'CHF': {'Nominal': 1, 'Name': 'Швейцарский франк', 'Value': 58.4749, 'Previous': 59.1517},
            'ZAR': {'Nominal': 10, 'Name': 'Южноафриканских рэндов', 'Value': 35.9579, 'Previous': 36.1323},
            'KRW': {'Nominal': 1000, 'Name': 'Вон Республики Корея', 'Value': 44.5197, 'Previous': 44.9921},
            'JPY': {'Nominal': 100, 'Name': 'Японских иен', 'Value': 44.3409, 'Previous': 44.5523}}
MAIN_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in MAIN_BUTTONS))
RATE_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in RATE_BUTTONS))
DELTA_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in DELTA_BUTTONS))
DELAY_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in DELAY_BUTTONS))

CURRENCY_NAME_CODE = {currency[key]['Name']: key for key in currency}
CURRENCY_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*CURRENCY_NAME_CODE.keys(), 'Назад')


async def update_currency():
    print('Обновление валюты начато')
    global currency
    global CURRENCY_NAME_CODE
    global CURRENCY_KEYBOARD
    if temp := get_currency():
        currency = temp
        CURRENCY_NAME_CODE = {currency[key]['Name']: key for key in currency}
        CURRENCY_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*CURRENCY_NAME_CODE.keys(), 'Назад')
        session = Session(bind=engine)
        subscribes = session.query(Subscribe).all()
        for subscribe in subscribes:
            if subscribe.value != currency[subscribe.code]['Value']:
                subscribe.value = currency[subscribe.code]['Value']
        session.commit()
        print('Обновление валюты завершено')
        return
    print('Ошибка обновления')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    session = Session(bind=engine)
    if not session.query(User).get(message.from_user.id):
        user = User(id=message.from_user.id, username=message.from_user.username)
        session.add(user)
        session.commit()
    session.close()
    if 'start' in message.text:
        await message.answer("Привет!\nЯ бот для отслеживания курса валюты.\n",
                             reply_markup=MAIN_KEYBOARD)


@dp.message_handler(filters.Text(equals='Назад'))
async def send_welcome(message: types.Message):
    await message.answer("Выберите действие", reply_markup=MAIN_KEYBOARD)


@dp.message_handler(filters.Text(equals='Настроить отслеживание'))
async def choose_rate(message: types.Message):
    await message.answer("Выберите тип отслеживания", reply_markup=RATE_KEYBOARD)


@dp.message_handler(filters.Text(equals=RATE_BUTTONS))
async def set_rate(message: types.Message):
    if message.text == RATE_BUTTONS[0]:
        await message.answer('Выберите время отслеживания', reply_markup=DELAY_KEYBOARD)
    elif message.text == RATE_BUTTONS[1]:
        await message.answer('Выберите изменение для отслеживания', reply_markup=DELTA_KEYBOARD)
    elif message.text == RATE_BUTTONS[2]:
        session = Session(bind=engine)
        subscribe_types = session.query(User).get(message.from_user.id).types
        text = ''
        if subscribe_types:
            for subscribe in subscribe_types:
                if subscribe.type == 1:
                    text += 'У вас установлено отслеживание по времени '
                    if subscribe.delay == 60:
                        text += 'раз в минуту.\n'
                    if subscribe.delay == 60 * 60:
                        text += 'раз в час.\n'
                    if subscribe.delay == 60 * 60 * 24:
                        text += 'раз в сутки.\n'
                if subscribe.type == 2:
                    text += 'У вас установлено отслеживание при изменении '
                    if subscribe.delta == 0.01:
                        text += 'на 1 копейку.\n'
                    if subscribe.delta == 0.1:
                        text += 'на 10 копеек.\n'
                    if subscribe.delta == 1:
                        text += 'на 1 рубль.\n'
        else:
            text += 'У вас нет ни одного активного отслеживания.'
        await message.answer(text, reply_markup=RATE_KEYBOARD)
        session.close()


@dp.message_handler(filters.Text(equals=DELAY_BUTTONS))
async def set_rate(message: types.Message):
    session = Session(bind=engine)
    subscribe_type = session.query(SubscribeType).filter(SubscribeType.type == 1,
                                                         SubscribeType.user_id == message.from_user.id).all()
    delay = None
    if message.text == DELAY_BUTTONS[0]:
        delay = 60
    elif message.text == DELAY_BUTTONS[1]:
        delay = 60 * 60
    elif message.text == DELAY_BUTTONS[2]:
        delay = 60 * 60 * 24
    elif message.text == DELAY_BUTTONS[3]:
        if subscribe_type:
            session.delete(subscribe_type[0])
            session.commit()
    elif message.text == DELAY_BUTTONS[4]:
        await message.answer("Выберите тип отслеживания", reply_markup=RATE_KEYBOARD)
        return

    if subscribe_type:
        subscribe_type[0].delay = delay
        session.commit()
    else:
        subscribe_type = SubscribeType(type=1, user_id=message.from_user.id, delay=delay, delta=None)
        session.add(subscribe_type)
        session.commit()

    subscribe_type = session.query(SubscribeType).filter(SubscribeType.type == 1,
                                                         SubscribeType.user_id == message.from_user.id).all()
    text = ''
    print(subscribe_type)
    if subscribe_type:
        for subscribe in subscribe_type:
            if subscribe.type == 1:
                text += 'У вас установлено отслеживание по времени '
                if subscribe.delay == 60:
                    text += 'раз в минуту.\n'
                if subscribe.delay == 60 * 60:
                    text += 'раз в час.\n'
                if subscribe.delay == 60 * 60 * 24:
                    text += 'раз в сутки.\n'
    else:
        text += 'У вас нет отслеживания по времени.'
    await message.answer(text, reply_markup=RATE_KEYBOARD)
    session.close()


@dp.message_handler(filters.Text(equals=DELTA_BUTTONS))
async def set_delta(message: types.Message):
    session = Session(bind=engine)
    subscribe_type = session.query(SubscribeType).filter(SubscribeType.type == 2,
                                                         SubscribeType.user_id == message.from_user.id).all()
    delta = None
    if message.text == DELTA_BUTTONS[0]:
        delta = 0.01
    elif message.text == DELTA_BUTTONS[1]:
        delta = 0.1
    elif message.text == DELTA_BUTTONS[2]:
        delta = 1
    elif message.text == DELTA_BUTTONS[3]:
        if subscribe_type:
            session.delete(subscribe_type[0])
            session.commit()
    elif message.text == DELTA_BUTTONS[4]:
        await message.answer("Выберите тип отслеживания", reply_markup=RATE_KEYBOARD)
        return

    if subscribe_type:
        subscribe_type[0].delta = delta
        session.commit()
    else:
        subscribe_type = SubscribeType(type=2, user_id=message.from_user.id, delay=None, delta=delta)
        session.add(subscribe_type)
        session.commit()

    subscribe_type = session.query(SubscribeType).filter(SubscribeType.type == 2,
                                                         SubscribeType.user_id == message.from_user.id).all()
    text = ''
    if subscribe_type:
        for subscribe in subscribe_type:
            if subscribe.type == 2:
                text += 'У вас установлено отслеживание при изменении '
                if subscribe.delta == 0.01:
                    text += 'на 1 копейку.\n'
                if subscribe.delta == 0.1:
                    text += 'на 10 копеек.\n'
                if subscribe.delta == 1:
                    text += 'на 1 рубль.\n'
    else:
        text += 'У вас нет ни одного активного отслеживания.'
    await message.answer(text, reply_markup=RATE_KEYBOARD)
    session.close()


@dp.message_handler(filters.Text(equals='Выбрать валюту'))
async def choose_currency(message: types.Message):
    session = Session(bind=engine)
    subscribes = session.query(User).get(message.from_user.id).subscribes
    if subscribes:
        text = "Вы отслеживате курс: " + ", ".join(sorted([subscribe.name for subscribe in subscribes])) + "\n"
        text += "Если хотите перестать отслеживать курс валюты нажмите на нее еще раз."
    else:
        text = "Вы не отслеживаете ни одного курса валюты."
    await message.answer(text, reply_markup=CURRENCY_KEYBOARD)


@dp.message_handler(filters.Text(equals=CURRENCY_NAME_CODE.keys()))
async def set_subscribe(message: types.Message):
    print('Отслеживание')
    session = Session(bind=engine)
    subscribe = session.query(Subscribe).get((CURRENCY_NAME_CODE[message.text], message.from_user.id))
    if not subscribe:
        subscribe = Subscribe(code=CURRENCY_NAME_CODE[message.text],
                              name=message.text,
                              nominal=currency[CURRENCY_NAME_CODE[message.text]]['Nominal'],
                              value=currency[CURRENCY_NAME_CODE[message.text]]['Value'],
                              previous=currency[CURRENCY_NAME_CODE[message.text]]['Value'],
                              user_id=message.from_user.id)
        session.add(subscribe)
        session.commit()
    else:
        session.delete(subscribe)
        session.commit()
    subscribes = session.query(User).get(message.from_user.id).subscribes
    if subscribes:
        text = "Вы отслеживате курс: " + ", ".join(
            sorted([subscribe.name for subscribe in subscribes])) + "\n"  # добавить сортировку
        text += "Если хотите перестать отслеживать курс валюты нажмите на нее еще раз."
    else:
        text = "Вы не отслеживаете ни одного курса валюты."
    await message.reply(text, reply_markup=CURRENCY_KEYBOARD)


@dp.message_handler(filters.Text(equals='Получить курс валюты'))
async def get_now_currency(message: types.Message):
    session = Session(bind=engine)
    subscribes = session.query(User).get(message.from_user.id).subscribes  # добавить сортировку
    text = ''
    if subscribes:
        for subscribe in subscribes:
            text += f"{subscribe.name} стоит {subscribe.value} рублей.\n"
    else:
        text = 'Вы не выбрали ни одну валюту для отслеживания.'
    await message.answer(text, reply_markup=MAIN_KEYBOARD)


async def send_currency():
    print('Начало рассылки')
    now = datetime.now()
    session = Session(bind=engine)
    user_type_subscribe_table = session.query(User, SubscribeType, Subscribe).filter(
        User.id == SubscribeType.user_id).filter(
        User.id == Subscribe.user_id).all()
    text = {}
    pprint(user_type_subscribe_table)
    print('Рассылка по времени')
    for user, subscribe_type, subscribe in user_type_subscribe_table:
        if subscribe_type.type == 1:
            if now - subscribe.updated_date >= timedelta(seconds=subscribe_type.delay):
                if user.id not in text:
                    text[user.id] = f"{subscribe.nominal} {subscribe.name} стоит {subscribe.value} рублей.\n"
                else:
                    text[user.id] += f"{subscribe.nominal} {subscribe.name} стоит {subscribe.value} рублей.\n"
                subscribe.updated_date = datetime.now()
    print(text)
    for user in text.keys():
        await bot.send_message(user, text[user])
    print('Рассылка по времени завершена.')
    print('Рассылка по разнице')
    for user, subscribe_type, subscribe in user_type_subscribe_table:
        if subscribe_type.type == 2:
            if abs(subscribe.value - subscribe.previous) >= subscribe_type.delta:
                text = f"Стоимость {subscribe.nominal} {subscribe.name} изменилась на {subscribe_type.delta} копеек/рублей.\n"
                text += f'Цена была {subscribe.previous}, цена стала {subscribe.value}'
                await bot.send_message(user.id, text)
                subscribe.previous = subscribe.value
        await asyncio.sleep(1)
    session.commit()
    print('Рассылка по разнице завершена.')


async def mainloop():
    while True:
        await update_currency()
        await asyncio.sleep(10)
        await send_currency()


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(mainloop())
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
