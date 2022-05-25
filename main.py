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

MAIN_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in MAIN_BUTTONS))
RATE_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in RATE_BUTTONS))
DELTA_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in DELTA_BUTTONS))
DELAY_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*(KeyboardButton(text) for text in DELAY_BUTTONS))

currency = get_currency()
if not currency:
    exit('Не смог получить курс валюты')
CURRENCY_NAME_CODE = {currency[key]['Name']: key for key in currency}
CURRENCY_KEYBOARD = ReplyKeyboardMarkup(row_width=1).add(*CURRENCY_NAME_CODE.keys(), 'Назад')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    session = Session(bind=engine)
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
                    if subscribe.delta == 1:
                        text += 'на 1 копейку.\n'
                    if subscribe.delta == 10:
                        text += 'на 10 копеек.\n'
                    if subscribe.delta == 100:
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
    await message.answer(text, reply_markup=DELAY_KEYBOARD)
    session.close()

@dp.message_handler(filters.Text(equals=DELTA_BUTTONS))
async def set_delta(message: types.Message):
    session = Session(bind=engine)
    subscribe_type = session.query(SubscribeType).filter(SubscribeType.type == 2,
                                                         SubscribeType.user_id == message.from_user.id).all()
    delta = None
    if message.text == DELTA_BUTTONS[0]:
        delta = 1
    elif message.text == DELTA_BUTTONS[1]:
        delta = 10
    elif message.text == DELTA_BUTTONS[2]:
        delta = 100
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
                if subscribe.delta == 1:
                    text += 'на 1 копейку.\n'
                if subscribe.delta == 10:
                    text += 'на 10 копеек.\n'
                if subscribe.delta == 100:
                    text += 'на 1 рубль.\n'
    else:
        text += 'У вас нет ни одного активного отслеживания.'
    await message.answer(text, reply_markup=DELTA_KEYBOARD)
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
async def set_currency(message: types.Message):
    session = Session(bind=engine)
    subscribe = session.query(Subscribe).get((CURRENCY_NAME_CODE[message.text], message.from_user.id))
    if not subscribe:
        subscribe = Subscribe(code=CURRENCY_NAME_CODE[message.text],
                              name=message.text,
                              value=currency[CURRENCY_NAME_CODE[message.text]]['Value'],
                              previous=currency[CURRENCY_NAME_CODE[message.text]]['Previous'],
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
async def get_currency(message: types.Message):
    session = Session(bind=engine)
    subscribes = session.query(User).get(message.from_user.id).subscribes  # добавить сортировку
    text = ''
    if subscribes:
        for subscribe in subscribes:
            text += f"{subscribe.name} стоит {subscribe.value} рублей.\n"
    else:
        text = 'Вы не выбрали ни одну валюту для отслеживания.'
    await message.answer(text, reply_markup=MAIN_KEYBOARD)


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
