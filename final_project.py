import pickle
import time
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN = '7189997896:AAElWTvmR-IF40N9890K-qzKFJC5Hpb2sME'

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# Словарь, в котором будут храниться данные пользователя
users = {}
CURRENT_WORD_ID = -1

# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        'Hi!\nI am a bot named Rembo!\n\n'
        'To get the list of availuble commands - send command /help')
    if message.from_user.id not in users:
        users[message.from_user.id] = {
            'in_game': False,
            'alph' : {}
        }
        await message.answer('Nice to meet you!')


# Этот хэндлер будет срабатывать на команду "/list"
@dp.message(Command(commands='list'))
async def process_stat_command(message: Message):
    if users[message.from_user.id]['in_game'] == False and users[message.from_user.id]['alph'] != {}:
        await message.answer(' '.join(list(users[message.from_user.id]['alph'].keys())))
    elif users[message.from_user.id]['in_game'] == False and users[message.from_user.id]['alph'] == {}:
        await message.answer('Your list is empty.')
    else:
        await message.answer ('You are in game now. Please, quit before with command /q.')

#Checking where the person now

# Этот хэндлер будет срабатывать на команду "/add"
@dp.message(lambda x: '/add' in x.text)
async def process_stat_command(message: Message):
    if users[message.from_user.id]['in_game'] == False:
        if message.text.split(',')[1] not in users[message.from_user.id]['alph']:
            users[message.from_user.id]['alph'][message.text.split(',')[1]] = message.text.split(',')[2]
            #await message.answer(' '.join(users[message.from_user.id]['alph'].keys()))
        else:
            await message.answer('This word is already in your list.')
    else:
        await message.answer ('You are in game now. Please, quit before with command /q.')


# Этот хэндлер будет срабатывать на команду "/del"
@dp.message(Command(commands='del'))
async def process_stat_command(message: Message):
    if users[message.from_user.id]['in_game'] == False:
        if message.text.split()[0] in users[message.from_user.id]['alph']:
            del users[message.from_user.id]['alph'][message.text.split()[0]]
        else:
            await message.answer('I could not find the word.')
    else:
        await message.answer ('You are in game now. Please, quit before with command /q.')


# Этот хэндлер будет срабатывать на команду "/show"
@dp.message(Command(commands='del'))
async def process_stat_command(message: Message):
    if users[message.from_user.id]['in_game'] == False:
        if message.text.split()[0] in users[message.from_user.id]['alph']:
            del users[message.from_user.id]['alph'][message.text.split()[0]]
        else:
            await message.answer('I could not find the word.')
    else:
        await message.answer ('You are in game now. Please, quit before with command /q.')


# Этот хэндлер будет срабатывать на команду "/q"
@dp.message(Command(commands='del'))
async def process_cancel_command(message: Message):
    if users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = False
        await message.answer(
            'You finished the game. If you want to do it again'
            '- write to me about.'
        )
    else:
        await message.answer(
            'We are not in game right now.'
        )


# Этот хэндлер будет срабатывать на на команду "/rembo"
@dp.message(Command(commands='rembo'))
async def process_positive_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['alph'] = dict(sorted(users[message.from_user.id]['alph'], reverse=True, key=lambda x: x[3]))
        await message.answer(
            'Hey!Let us start the game!'
        )
        CURRENT_WORD_ID = -1
        await message.answer(users[message.from_user.id]['alph'][CURRENT_WORD_ID])
    else:
        await message.answer(
            'While we are playing this game'
            'I can reflect only these command: /q, yes, no'
        )


# Этот хэндлер будет срабатывать на отправку пользователем yes, no
@dp.message(lambda x: x.text and x.text in ['yes', 'no'])
async def process_numbers_answer(message: Message):
    if users[message.from_user.id]['in_game']:
        if message.text=='yes':
            await message.answer('You are breathtaking! But I remember you the meaning\n'
                                f'{users[message.from_user.id]['alph'].keys()[CURRENT_WORD_ID]} - '
                                f'{users[message.from_user.id]['alph'].values()[CURRENT_WORD_ID]}')
            users[message.from_user.id]['alph'][CURRENT_WORD_ID][-1] += 1
            CURRENT_WORD_ID -= 1
            await time.sleep(1)
            await message.answer(users[message.from_user.id]['alph'][CURRENT_WORD_ID])
    else:
        await message.answer('We are still not in game. Do you want to play? Send me /rembo to start')



# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_answers(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer(
            'We are not in game right now.')
    else:
        await message.answer(
            'I am a not so clever. What exactly do you want to do?'
        )


if __name__ == '__main__':
    dp.run_polling(bot)