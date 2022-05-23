import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import filters
from aiogram.types import Message
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from exchange_rate.exchange_rate import get_rate

from os import getenv
from sys import exit

# Configure logging
logging.basicConfig(level=logging.INFO)

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

main_buttons = ('Выбрать валюту',
                'Настроить отслеживание',
                'Помощь')

rate_buttons = ('Отслеживание по времени',
                'Отслеживание при изменении',
                'Отслеживание при запросе',
                'Назад')

main_keyboard = ReplyKeyboardMarkup(row_width=1)
main_keyboard.add(*(KeyboardButton(text) for text in main_buttons))
rate_keyboard = ReplyKeyboardMarkup(row_width=1)
rate_keyboard.add(*(KeyboardButton(text) for text in rate_buttons))


@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    # logging.debug(Message.text)
    await message.reply("Привет!\nЯ бот для отслеживания курса валюты\nДля помощи отправь /help.")


@dp.message_handler(commands=['help'])
async def send_welcome(message: Message):
    await message.reply("Справка")


@dp.message_handler(filters.Text(equals='Настроить отслеживание'))
async def echo(message: Message):
    # logging.debug(Message.text)
    await message.reply("Выбери действие", reply_markup=rate_keyboard)


@dp.message_handler()
async def echo(message: Message):
    # logging.debug(Message.text)
    await message.reply("Выбери действие", reply_markup=main_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
