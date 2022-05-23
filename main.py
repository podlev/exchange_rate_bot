import logging
import json

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
print(get_rate_exchange())
currency_name_code = {rate_exchange[key]['Name']: key for key in rate_exchange}


def init_user(id):
    users[id] = {'currency': [], 'type': 0}


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    init_user(message.from_user.id)
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
        await message.answer("Данная функция временно недоступна")
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
    currency_text = [rate_exchange[key]['Name'] for key in users[message.from_user.id]['currency']]
    if currency_text:
        text = "Вы отслеживате курс: " + ", ".join(currency_text) + "\n"
        text += "Если хотите перестать отслеживать курс валюты нажмите на нее еще раз."
    else:
        text = "Вы не отслеживаете ни одного курса вылюты."
    await message.reply(text, reply_markup=exchange_keyboard)


@dp.message_handler(filters.Text(equals=tuple(currency_name_code.keys())))
async def set_currency(message: types.Message):
    if message.from_user.id not in users:
        init_user(message.from_user.id)
    if currency_name_code[message.text] in users[message.from_user.id]['currency']:
        users[message.from_user.id]['currency'].remove(currency_name_code[message.text])
    else:
        users[message.from_user.id]['currency'].append(currency_name_code[message.text])
    print(users)
    exchange_keyboard = ReplyKeyboardMarkup(row_width=1)
    buttons = tuple(currency_name_code.keys())
    exchange_keyboard.add(*buttons, 'Назад')
    currency_text = [rate_exchange[key]['Name'] for key in users[message.from_user.id]['currency']]
    if currency_text:
        text = "Вы отслеживате курс: " + ", ".join(currency_text) + "\n"
        text += "Если хотите перестать отслеживать курс валюты нажмите на нее еще раз."
    else:
        text = "Вы не отслеживаете ни одного курса вылюты."
    await message.reply(text, reply_markup=exchange_keyboard)


@dp.message_handler(filters.Text(equals='Получить курс валюты'))
async def choose_currency(message: types.Message):
    text = ''
    if users[message.from_user.id]['currency']:
        for Code in users[message.from_user.id]['currency']:
            text += f"{rate_exchange[Code]['Nominal']} {rate_exchange[Code]['Name']} стоит {rate_exchange[Code]['Value']} рублей.\n"
    else:
        text = 'Вы не выбрали ни одну валюту для отслеживания.'
    await message.answer(text, reply_markup=main_keyboard)


# @dp.message_handler()
# async def echo(message: types.Message):
#     print(message.text)
#     print(tuple(currency_name_code.keys()))
#


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
