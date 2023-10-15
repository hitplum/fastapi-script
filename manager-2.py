
import asyncio

from fastapi import FastAPI
from fastapi_script import Manager, Command, Option

app = FastAPI()
manager = Manager(app)


class HelloCommand(Command):

    def get_options(self):
        return [
            Option('-n', '--name', dest='name', help='input your name'),
            Option('-s', '--score', dest='score', help='input your score')
        ]

    async def run(self, *args, **kwargs):
        print(f'hello command, args: {args}, kwargs: {kwargs}')


manager.add_command('hello', HelloCommand())

if __name__ == '__main__':
    asyncio.run(manager.run())