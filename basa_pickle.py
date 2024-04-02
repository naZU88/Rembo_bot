import asyncio
import pickle
import time

#################


def open_dict():
    try:
        with open('data.pickle', 'rb') as f:
            user: dict = pickle.load(f)
        return user if isinstance(user, dict) else None
    except FileNotFoundError:
        user: dict = {}
        return user
    except Exception as e:
        print('Словарь прочитан с ошибками', e)
    finally:
        pass

#################

async def dump():
    while True:
        print(user)
        with open('data.pickle', 'wb') as f:
            pickle.dump(user, f)
        await asyncio.sleep(10)


async def on_startup(x):
    asyncio.create_task(dump())


if __name__ == '__main__':
    user = open_dict()
    if user != None:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)