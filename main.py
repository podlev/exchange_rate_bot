import datetime
import logging
import json
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from exchange_rate.exchange_rate import get_rate_exchange

from os import getenv
from sys import exit

# Configure logging

# logging.basicConfig(filename='log.log',
#                     filemode='w',
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO,
#                     datefmt='%d-%b-%y %H:%M:%S')

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

main_buttons = ('Получить курс валюты',
                'Выбрать валюту',
                'Настроить отслеживание',
                'Помощь')

rate_buttons = ('Отслеживание по времени',
                'Отслеживание при изменении',
                'Отслеживание при запросе',
                'Назад')

try:
    with open('users.json') as json_file:
        users = json.load(json_file)
except Exception as e:
    print(e)
    users = {}
    with open('users.json', 'w') as json_file:
        json.dump(users, json_file)

main_keyboard = ReplyKeyboardMarkup(row_width=1)
main_keyboard.add(*(KeyboardButton(text) for text in main_buttons))
rate_keyboard = ReplyKeyboardMarkup(row_width=1)
rate_keyboard.add(*(KeyboardButton(text) for text in rate_buttons))

rate_exchange = get_rate_exchange()
currency_name_code = {rate_exchange[key]['Name']: key for key in rate_exchange}


async def update_currency():
    global rate_exchange
    rate_exchange = get_rate_exchange()


async def init_user(id):
    users[id] = {'currency': [], 'type': 0, 'delay': None, 'last_update': None}


async def save_settings():
    with open('users.json', 'w') as json_file:
        json.dump(users, json_file, default=str)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await init_user(str(message.from_user.id))
    if 'start' in message.text:
        await message.answer("Привет!\nЯ бот для отслеживания курса валюты\nДля помощи отправь /help.",
                             reply_markup=main_keyboard)
    elif 'help' in message.text:
        await message.answer("Справка", reply_markup=main_keyboard)


@dp.message_handler(filters.Text(equals='Назад'))
async def send_welcome(message: types.Message):
    await message.answer("Выбери действие", reply_markup=main_keyboard)


@dp.message_handler(filters.Text(equals='Настроить отслеживание'))
async def choose_rate(message: types.Message):
    await message.reply("Выбери действие", reply_markup=rate_keyboard)


@dp.message_handler(filters.Text(equals=rate_buttons))
async def set_rate(message: types.Message):
    if message.text == 'Отслеживание по времени':
        users[str(message.from_user.id)]['type'] = 1
        users[str(message.from_user.id)]['delay'] = 1
        users[str(message.from_user.id)]['last_update'] = datetime.datetime.now()
        await save_settings()
        await message.answer("Установил отслеживание каждую минуту", reply_markup=main_keyboard)
    if message.text == 'Отслеживание при изменении':
        await message.answer("Данная функция временно недоступна")
    if message.text == 'Отслеживание при запросе':
        await message.answer("Данная функция временно недоступна")
    await message.answer("Выбери действие", reply_markup=rate_keyboard)


@dp.message_handler(filters.Text(equals='Выбрать валюту'))
async def choose_currency(message: types.Message):
    exchange_keyboard = ReplyKeyboardMarkup(row_width=1)
    buttons = tuple(currency_name_code.keys())
    exchange_keyboard.add(*buttons, 'Назад')
    currency_text = [rate_exchange[key]['Name'] for key in users[str(message.from_user.id)]['currency']]
    if currency_text:
        text = "Вы отслеживате курс: " + ", ".join(currency_text) + "\n"
        text += "Если хотите перестать отслеживать курс валюты нажмите на нее еще раз."
    else:
        text = "Вы не отслеживаете ни одного курса вылюты."
    await message.reply(text, reply_markup=exchange_keyboard)


@dp.message_handler(filters.Text(equals=tuple(currency_name_code.keys())))
async def set_currency(message: types.Message):
    if str(message.from_user.id) not in users:
        await init_user(str(message.from_user.id))
    if currency_name_code[message.text] in users[str(message.from_user.id)]['currency']:
        users[str(message.from_user.id)]['currency'].remove(currency_name_code[message.text])
    else:
        users[str(message.from_user.id)]['currency'].append(currency_name_code[message.text])
    print(users)
    exchange_keyboard = ReplyKeyboardMarkup(row_width=1)
    buttons = tuple(currency_name_code.keys())
    exchange_keyboard.add(*buttons, 'Назад')
    currency_text = [rate_exchange[key]['Name'] for key in users[str(message.from_user.id)]['currency']]
    if currency_text:
        text = "Вы отслеживате курс: " + ", ".join(currency_text) + "\n"
        text += "Если хотите перестать отслеживать курс валюты нажмите на нее еще раз."
    else:
        text = "Вы не отслеживаете ни одного курса вылюты."
    await save_settings()
    await message.reply(text, reply_markup=exchange_keyboard)


@dp.message_handler(filters.Text(equals='Получить курс валюты'))
async def get_currency(message: types.Message):
    text = ''
    if users[str(message.from_user.id)]['currency']:
        for Code in users[str(message.from_user.id)]['currency']:
            text += f"{rate_exchange[Code]['Nominal']} {rate_exchange[Code]['Name']} стоит {rate_exchange[Code]['Value']} рублей.\n"
    else:
        text = 'Вы не выбрали ни одну валюту для отслеживания.'
    await message.answer(text, reply_markup=main_keyboard)


async def send_currency():
    now = datetime.datetime.now()
    for user_id in users:
        print(user_id)
        if users[user_id]['type'] == 1:
            last_update = datetime.datetime.strptime(users[user_id]['last_update'], '%Y-%m-%d %H:%M:%S.%f')
            print(now - last_update > datetime.timedelta(seconds=users[user_id]['delay'] * 60))
            if (now - last_update) > datetime.timedelta(seconds=users[user_id]['delay'] * 60):
                text = ''
                if users[user_id]['currency']:
                    for Code in users[user_id]['currency']:
                        text += f"{rate_exchange[Code]['Nominal']} {rate_exchange[Code]['Name']} стоит {rate_exchange[Code]['Value']} рублей.\n"
                else:
                    text = 'Вы не выбрали ни одну валюту для отслеживания.'
                await bot.send_message(int(user_id), text)


async def mainloop():
    while True:
        await asyncio.sleep(10)
        await update_currency()
        await send_currency()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(mainloop())
    executor.start_polling(dp, skip_updates=True)
