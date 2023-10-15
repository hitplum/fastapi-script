
import asyncio

from fastapi import FastAPI
from fastapi_script import Manager


app = FastAPI()
manager = Manager(app)

@manager.command
async def test_without_params():
    print('test_without_params')

@manager.command
async def test_one_params(name):
    print(f'test_one_params, name: {name}')

@manager.command
async def test_many_params(name, age=0):
    print(f'test_many_params, name: {name}, age: {age}')

@manager.option('-n', '--name', dest='name', help='input your name')
async def option_one_params(name):
    print(f'option_one_params, name: {name}')

@manager.option('-n', '--name', dest='name', help='input your name')
@manager.option('-s', '--score', dest='score', help='input your score')
async def option_many_params(name, score):
    print(f'option_many_params, name: {name}, score: {score}')


if __name__ == '__main__':
    asyncio.run(manager.run())
