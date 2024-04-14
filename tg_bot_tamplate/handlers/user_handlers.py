import json
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter
import requests
from keyboards.keyboards import yes_no_quit_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

API_CATS_URL = 'https://api.thecatapi.com/v1/images/search'
CURRENT_WORD_ID = -1
router = Router()


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    add_word = State()
    add_using = State()
    show_word = State()
    delete_word = State()
    in_quiz = State()


# Этот хэндлер будет срабатывать на команду "/start"
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
    users_id = [id['user_id'] for id in data]
    if message.from_user.id not in users_id:
        new_user = {
            'user_id': message.from_user.id,
            'voc' : {}
        }
        data.append(new_user)
        with open('tg_bot_tamplate/data/users_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    await message.answer(
        'Hi!\nI am a bot named Rembo!\n\n'
        'To get the list of availuble commands - click on the menu.')


# Этот хэндлер будет срабатывать на команду "/list"
@router.message(Command(commands='list'), StateFilter(default_state))
async def process_list_command(message: Message):
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            if user["voc"] != {}:
                await message.answer('\n'.join(list(user["voc"].keys())))
            else:
                await message.answer('Your vocabulary is empty. Please, add some new words.')


# Этот хэндлер будет срабатывать на команду "/show"
@router.message(Command(commands='show'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Please, write down your word/phrase.')
    await state.set_state(FSMFillForm.show_word)


@router.message(StateFilter(FSMFillForm.show_word))
async def process_name_sent(message: Message, state: FSMContext):
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
    for user in data:
            if user["user_id"] == message.from_user.id:
                vocabulary=user['voc'].keys()
                if message.text in vocabulary:
                    definition = user['voc'][message.text][0]
                    using = user['voc'][message.text][1]
                    await message.answer(text=f'{message.text} - {definition} - index {using}')
                else:
                    await message.answer(text='This word/phrase is not in your vocabulary. Try again.')
    await state.clear()



@router.message(Command(commands='show'), StateFilter(FSMFillForm.show_word))
async def process_fillform_command(message: Message):
    await message.answer(text='This word/phrase is not in your vocabulary. Try again.')



# Этот хэндлер будет срабатывать на команду /add
@router.message(Command(commands='add'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Please, write down your word or phrase')
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            await state.update_data(vocabulary=user['voc'].keys())
    await state.set_state(FSMFillForm.add_word)


@router.message(StateFilter(FSMFillForm.add_word), lambda x: x.text.replace(' ', '').isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
    for user in data:
            if user["user_id"] == message.from_user.id:
                vocabulary=user['voc'].keys()
                if message.text not in vocabulary:
                    await message.answer(text='Please, write down the using.')
                    await state.update_data(word=message.text)
                    await state.set_state(FSMFillForm.add_using)
                else:
                    await message.answer(text='This word/phrase is already in your vocabulary. Try again.')
                    await state.clear()


@router.message(StateFilter(FSMFillForm.add_word))
async def process_name_sent(message: Message):
    await message.answer(text='This word/phrase is not correct or already exist. Try again.')


@router.message(StateFilter(FSMFillForm.add_using), lambda x: x.text.replace(' ', '').isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
        for user in data:
            if user["user_id"] == message.from_user.id:
                data_dict = await state.get_data()
                user["voc"][data_dict['word']] = [message.text, 0]
                with open('tg_bot_tamplate/data/users_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
    await message.answer(text='Saved!')
    await state.clear()


@router.message(StateFilter(FSMFillForm.add_using))
async def process_name_sent(message: Message):
    await message.answer(text='This phrase is not correct. Try again.')



# Этот хэндлер будет срабатывать на команду "/del"
@router.message(Command(commands='del'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Please, write down your word or phrase')
    await state.set_state(FSMFillForm.delete_word)


@router.message(StateFilter(FSMFillForm.delete_word), lambda x: x.text.replace(' ', '').isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
        for user in data:
            if user["user_id"] == message.from_user.id:
                if message.text in user["voc"].keys():
                    del user["voc"][message.text]
                    with open('tg_bot_tamplate/data/users_data.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    await message.answer(text='Deleted!')
                else:
                    await message.answer(text='This word/phrase is not exist. Try again.')
    await state.clear()


@router.message(StateFilter(FSMFillForm.delete_word))
async def process_name_sent(message: Message, state: FSMContext):
    await message.answer(text='This word/phrase is not correct or not exist. Try again.')



# Этот хэндлер будет срабатывать на команду "/quit" в состоянии
# по умолчанию
@router.message(Command(commands='quit'), StateFilter(default_state))
async def process_quit_command(message: Message):
    await message.answer(
        text='You are not in quiz now'
    )


# Этот хэндлер будет срабатывать на команду "/quit" в любых состояниях,
# кроме состояния по умолчанию
@router.message(Command(commands='quit'), ~StateFilter(default_state))
async def process_quit_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='You left the state.\n'
        'To get the list of availuble commands - click on the menu.'
    )
    await state.clear()


# Этот хэндлер будет срабатывать на на команду "/rembo"
@router.message(Command(commands='rembo'), StateFilter(default_state))
async def process_rembo_answer(message: Message, state: FSMContext):
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            user["voc"] = dict(sorted(user["voc"].items(), reverse=True, key=lambda x: x[1][-1]))
            words = list(user["voc"].keys())
            with open('tg_bot_tamplate/data/users_data.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
    await message.answer('Hey! Let us start the quiz!')
    CURRENT_WORD_ID = -1
    await message.answer(text=f"{words[CURRENT_WORD_ID]}", reply_markup=yes_no_quit_keyboard)
    await state.set_state(FSMFillForm.in_quiz)



# Этот хэндлер будет срабатывать на отправку пользователем yes, no, finish
@router.message(StateFilter(FSMFillForm.in_quiz), lambda x: x.text and x.text in ['yes', 'no', 'finish'])
async def process_numbers_answer(message: Message, state: FSMContext):
    with open('tg_bot_tamplate/data/users_data.json') as file:
        data = json.load(file)
    for user in data:
        if user["user_id"] == message.from_user.id:
            if message.text=='yes':
                user["voc"][CURRENT_WORD_ID][-1] += 1
                CURRENT_WORD_ID -= 1
                with open('tg_bot_tamplate/data/users_data.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
            elif message.text=='no':
                user["voc"][CURRENT_WORD_ID][-1] -= 1
                CURRENT_WORD_ID -= 1
                with open('tg_bot_tamplate/data/users_data.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
            else:
                await message.answer(
                    'You finished the game. Congratulations! Hold the cat!'
                )
                cat_response = requests.get(API_CATS_URL)
                if cat_response.status_code == 200:
                    cat_link = cat_response.json()[0]['url']
                    await message.answer(cat_link)
                await state.clear()


@router.message(StateFilter(FSMFillForm.in_quiz))
async def process_name_sent(message: Message):
    await message.answer(text='While we are playing this game'
                    'I can reflect only these command: quit, yes, no')



# Этот хэндлер будет all the time
@router.message(StateFilter(default_state))
async def unknown_command(message: Message):
    await message.answer(
        text='Sorry, I can not get you.\n'
        'To get the list of availuble commands - click on the menu.'
    )