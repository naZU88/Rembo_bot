from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_yes = KeyboardButton(text='yes')
button_no = KeyboardButton(text='no')
button_finish = KeyboardButton(text='finish')

yes_no_quit_keyboard = ReplyKeyboardMarkup(keyboard=[[button_no, button_finish, button_yes]], resize_keyboard=True, one_time_keyboard=True)
