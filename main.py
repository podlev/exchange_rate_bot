from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from exchange_rate.exchange_rate import get_currency
# from database.models import User, Subscribe
from database.db import engine, User, Subscribe
from sqlalchemy.orm import Session

from os import getenv
from sys import exit

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

MAIN_BUTTONS = ('Получить курс валюты',
                'Выбрать валюту',
                'Настроить отслеживание',
                'Помощь')

RATE_BUTTONS = ('Отслеживание по времени',
                'Отслеживание при изменении',
                'Отслеживание при запросе',
                'Назад')

MAIN_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in MAIN_BUTTONS))
RATE_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in RATE_BUTTONS))

currency = get_currency()
CURRENCY_NAME_CODE = {currency[key]['Name']: key for key in currency}
CURRENCY_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*CURRENCY_NAME_CODE.keys(), 'Назад')

session = Session(bind=engine)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):

    if not session.query(User).get(message.from_user.id):
        user = User(id=message.from_user.id, username=message.from_user.username)
        session.add(user)
        session.commit()

    if 'start' in message.text:
        await message.answer("Привет!\nЯ бот для отслеживания курса валюты\nДля помощи отправь /help.",
                             reply_markup=MAIN_KEYBOARD)
    elif 'help' in message.text:
        await message.answer("Справка", reply_markup=MAIN_KEYBOARD)


@dp.message_handler(filters.Text(equals='Назад'))
async def send_welcome(message: types.Message):
    await message.answer("Выбери действие", reply_markup=MAIN_KEYBOARD)


@dp.message_handler(filters.Text(equals='Настроить отслеживание'))
async def choose_rate(message: types.Message):
    await message.answer("Выбери действие", reply_markup=RATE_KEYBOARD)


@dp.message_handler(filters.Text(equals=RATE_BUTTONS))
async def set_rate(message: types.Message):
    if message.text == 'Отслеживание по времени':
        await message.answer('Данная функция временно недоступна')
    if message.text == 'Отслеживание при изменении':
        await message.answer('Данная функция временно недоступна')
    if message.text == 'Отслеживание при запросе':
        await message.answer('Данная функция временно недоступна')
    await message.answer("Выбери действие", reply_markup=RATE_KEYBOARD)


@dp.message_handler(filters.Text(equals='Выбрать валюту'))
async def choose_currency(message: types.Message):
    # subscribes = session.query(Subscribe).filter(Subscribe.user_id == message.from_user.id).all()
    subscribes = session.query(User).get(message.from_user.id).subscribes
    print(subscribes)
    if subscribes:
        text = "Вы отслеживате курс: " + ", ".join([subscribe.name for subscribe in subscribes]) + "\n"
        text += "Если хотите перестать отслеживать курс валюты нажмите на нее еще раз."
    else:
        text = "Вы не отслеживаете ни одного курса вылюты."
    await message.reply(text, reply_markup=CURRENCY_KEYBOARD)

@dp.message_handler(filters.Text(equals=tuple(CURRENCY_NAME_CODE.keys())))
async def set_currency(message: types.Message):
    # if str(message.from_user.id) not in users:
    #     await init_user(str(message.from_user.id))
    # if currency_name_code[message.text] in users[str(message.from_user.id)]['currency']:
    #     users[str(message.from_user.id)]['currency'].remove(currency_name_code[message.text])
    # else:
    #     users[str(message.from_user.id)]['currency'].append(currency_name_code[message.text])
    # print(users)
    # exchange_keyboard = ReplyKeyboardMarkup(row_width=1)
    # buttons = tuple(currency_name_code.keys())
    # exchange_keyboard.add(*buttons, 'Назад')
    # currency_text = [rate_exchange[key]['Name'] for key in users[str(message.from_user.id)]['currency']]
    # if currency_text:
    #     text = "Вы отслеживате курс: " + ", ".join(currency_text) + "\n"
    #     text += "Если хотите перестать отслеживать курс валюты нажмите на нее еще раз."
    # else:
    #     text = "Вы не отслеживаете ни одного курса вылюты."
    # await save_settings()
    await message.reply('Данная функция временно недоступна', reply_markup=CURRENCY_KEYBOARD)


@dp.message_handler(filters.Text(equals='Получить курс валюты'))
async def get_currency(message: types.Message):
    # text = ''
    # if users[str(message.from_user.id)]['currency']:
    #     for Code in users[str(message.from_user.id)]['currency']:
    #         text += f"{rate_exchange[Code]['Nominal']} {rate_exchange[Code]['Name']} стоит {rate_exchange[Code]['Value']} рублей.\n"
    # else:
    #     text = 'Вы не выбрали ни одну валюту для отслеживания.'
    await message.answer('Данная функция временно недоступна', reply_markup=MAIN_KEYBOARD)


# async def send_currency():
#     now = datetime.datetime.now()
#     for user_id in users:
#         print(user_id)
#         if users[user_id]['type'] == 1:
#             last_update = datetime.datetime.strptime(users[user_id]['last_update'], '%Y-%m-%d %H:%M:%S.%f')
#             print(now - last_update > datetime.timedelta(seconds=users[user_id]['delay'] * 60))
#             if (now - last_update) > datetime.timedelta(seconds=users[user_id]['delay'] * 60):
#                 text = ''
#                 if users[user_id]['currency']:
#                     for Code in users[user_id]['currency']:
#                         text += f"{rate_exchange[Code]['Nominal']} {rate_exchange[Code]['Name']} стоит {rate_exchange[Code]['Value']} рублей.\n"
#                 else:
#                     text = 'Вы не выбрали ни одну валюту для отслеживания.'
#                 await bot.send_message(int(user_id), text)


# async def mainloop():
#     while True:
#         await asyncio.sleep(10)
#         await update_currency()
#         await send_currency()


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.create_task(mainloop())
    executor.start_polling(dp, skip_updates=True)
