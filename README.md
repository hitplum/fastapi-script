# FastAPI-Script
An extension for FastAPI.

## Getting Started

### Installation
First you have to install `fastapi-script` like this:
```bash
pip install fastapi-script
```
### Quick Tutorial
We need to create a Python module to manage your script commands, such as `manage.py`: 
```python
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
```
Next, we can manipulate the above script like this:
```bash
$ python manage.py test_without_params
test_with_no_param

$ python manage.py test_one_params laozhang
test_one_params, name: laozhang

$ python manage.py test_many_params laozhang --age 20
test_many_params, name: laozhang, age: 20

$ python manage.py option_one_params -n laozhang
option_one_params, name: laozhang

$ python manage.py option_one_params --name laozhang
option_one_params, name: laozhang

$ python manage.py option_many_params -n laozhang -s 90
option_many_params, name: laozhang, score: 90

$ python manage.py option_many_params --name laozhang --score 90
option_many_params, name: laozhang, score: 90
```
We can use the `--help` parameter to view all of the currently managed commands:
```bash
python manage.py --help
```
In addition to using the decorator above, we can also use the inherited Command class to do this：
```python
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

    def run(self, *args, **kwargs):
        print(f'hello command, args: {args}, kwargs: {kwargs}')


manager.add_command('hello', HelloCommand())

if __name__ == '__main__':
    asyncio.run(manager.run())
```
And then we can use it like this：
```bash
$ python manage.py hello -n laozhang -s 90
hello command, args: (), kwargs: {'name': 'laozhang', 'score': '90'}
```

