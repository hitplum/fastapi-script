import os
import sys
import string
import shutil
from pathlib import Path

from uvicorn import Config
from uvicorn import Server
from uvicorn.supervisors import ChangeReload

from .commands import Command, Option

dir_name = os.path.dirname(os.path.abspath(__file__))


def render_template(path, **kwargs):
    path_obj = Path(path)
    raw = path_obj.read_text('utf-8')
    content = string.Template(raw).substitute(**kwargs)
    render_path = path_obj.with_suffix("") if path_obj.suffix == '.tmpl' else path_obj
    if path_obj.suffix == '.tmpl':
        path_obj.rename(render_path)

    render_path.write_text(content, 'utf8')


class GenCommand(Command):

    def get_options(self):
        return [Option('module_name', type=str)]

    async def run(self, *args, **kwargs):
        module_name = kwargs['module_name']
        capitalized_module = ''.join(s.capitalize() for s in module_name.split("_"))
        vars = {
            'classname': f'{capitalized_module}Command'
        }
        command_file_path = f'{Path(".") / module_name}.py'
        shutil.copyfile(f"{dir_name}/command.tmpl", command_file_path)
        render_template(command_file_path, **vars)


class RunServerCommand(Command):

    def get_options(self):
        return [
            Option('-h', '--host', dest='host', type=str, default='127.0.0.1'),
            Option('-p', '--port', dest='port', type=int, default=8000),
            Option('--reload', dest='reload', action='store_true', default=True),
            Option('--workers', dest='workers', type=int, default=None)
        ]


    def get_main_module(self):
        # 获取启动文件的文件名
        if len(sys.argv) > 0:
            startup_file = sys.argv[0]
        else:
            startup_file = os.path.basename(__file__)

        return startup_file[:-3]

    def run(self,  *args, **kwargs):
        config = Config(app=f"{self.get_main_module()}:app", **kwargs)
        self.server = Server(config=config)
        if kwargs['reload']:
            sock = config.bind_socket()
            ChangeReload(config, target=self.server.run, sockets=[sock]).run()
        else:
            self.server.run()
