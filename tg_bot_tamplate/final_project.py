import json
import pickle
import time
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
import requests

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN = '7189997896:AAElWTvmR-IF40N9890K-qzKFJC5Hpb2sME'
API_CATS_URL = 'https://api.thecatapi.com/v1/images/search'
# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

CURRENT_WORD_ID = -1



# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        'Hi!\nI am a bot named Rembo!\n\n'
        'To get the list of availuble commands - send command /help')
    with open('users_data.json') as file:
        data = json.load(file)
    users_id = [id['user_id'] for id in data]
    if message.from_user.id not in users_id:
        new_user = {
            'user_id': message.from_user.id,
            'in_game': False,
            'voc' : {}
        }
        data.append(new_user)
        with open('users_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        await message.answer('Nice to meet you!')


# Этот хэндлер будет срабатывать на команду "/list"
@dp.message(lambda x: '/list' in x.text)
async def process_list_command(message: Message):
    with open('users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            if user["in_game"] == False and user["voc"] != {}:
                await message.answer(' '.join(list(user["voc"].keys())))
            elif user["in_game"] == False and user["voc"]  == {}:
                await message.answer('Your list is empty. Please, add some new words.')
            else:
                await message.answer ('You are in game now. Please, quit before with command /q.')

#Checking where the person now

# Этот хэндлер будет срабатывать на команду "/add"
@dp.message(lambda x: '/add' in x.text)
async def process_add_command(message: Message):
    with open('users_data.json') as file:
        data = json.load(file)
        for user in data:
            if user["user_id"] == message.from_user.id:
                if user["in_game"] == False:
                    if message.text.split(',')[1] not in user["voc"]:
                        user["voc"][message.text.split()[0]] = message.text.split(',')[2]
                        #await message.answer(' '.join(users[message.from_user.id]["voc"].keys()))
                        with open('users_data.json', 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2)
                    else:
                        await message.answer('This word is already in your list.')
                else:
                    await message.answer('You are in game now. Please, quit before with command /q.')


# Этот хэндлер будет срабатывать на команду "/del"
@dp.message(Command(commands='del'))
async def process_del_command(message: Message):
    with open('users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            if user["in_game"] == False:
                if message.text.split()[0] in user["voc"]:
                    del user["voc"][message.text.split()[0]]
                else:
                    await message.answer('I could not find the word.')
            else:
                await message.answer('You are in game now. Please, quit before with command /q.')


# Этот хэндлер будет срабатывать на команду "/q"
@dp.message(Command(commands='q'))
async def process_q_command(message: Message):
    with open('users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            if user['in_game']:
                user['in_game'] = False
                await message.answer(
                    'You finished the game. Congratulations! Hold the cat!'
                )
                cat_response = requests.get(API_CATS_URL)
                if cat_response.status_code == 200:
                    cat_link = cat_response.json()[0]['url']
                    await message.answer(cat_link)
            else:
                await message.answer(
                    'We are not in game right now.'
                )


# Этот хэндлер будет срабатывать на на команду "/rembo"
@dp.message(Command(commands='rembo'))
async def process_rembo_answer(message: Message):
    with open('users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            if not user['in_game']:
                user['in_game'] = True
                user["voc"] = dict(sorted(user["voc"], reverse=True, key=lambda x: x[3]))
                await message.answer(
                    'Hey!Let us start the game!'
                )
                CURRENT_WORD_ID = -1
                await message.answer(user["voc"][CURRENT_WORD_ID])
            else:
                await message.answer(
                    'While we are playing this game'
                    'I can reflect only these command: /q, y, n'
                )


# Этот хэндлер будет срабатывать на отправку пользователем y, n
@dp.message(lambda x: x.text and x.text in ['y', 'n'])
async def process_numbers_answer(message: Message):
    with open('users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            if user['in_game']:
                if message.text=='y':
                    await message.answer('You are breathtaking! But I remember you the meaning\n'
                                        f'{user["voc"].keys()[CURRENT_WORD_ID]} - '
                                        f'{user["voc"].values()[CURRENT_WORD_ID]}')
                    user["voc"][CURRENT_WORD_ID][-1] += 1
                    CURRENT_WORD_ID -= 1
                    await time.sleep(1)
                    await message.answer(user["voc"][CURRENT_WORD_ID])
            else:
                await message.answer('We are still not in game. Do you want to play? Send me /rembo to start')



# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_answers(message: Message):
    with open('users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            await message.answer(
                'We are not in game right now.')
        else:
            await message.answer(
                'I am a not so clever. What exactly do you want to do?'
            )


if __name__ == '__main__':
    dp.run_polling(bot)