
import re
import os
import sys
import argparse
from types import MethodType
from collections import OrderedDict

from .defaults import GenCommand, RunServerCommand
from .commands import Option, Command, add_help


safe_actions = (argparse._StoreAction,
                argparse._StoreConstAction,
                argparse._StoreTrueAction,
                argparse._StoreFalseAction,
                argparse._AppendAction,
                argparse._AppendConstAction,
                argparse._CountAction)


class Manager(object):

    help_args = ('-?', '--help')

    def __init__(self, app=None, usage=None, help=None, description=None):
        self.app = app
        self.usage = usage
        self.help = help
        self.description = description
        self.parent = None
        self._options = list()
        self.subparser_kwargs = dict()
        self._commands = OrderedDict()


    async def get_options(self):
        return self._options

    def add_command(self, *args, **kwargs):
        if len(args) == 1:
            command = args[0]
            name = None
        else:
            name, command = args

        if name is None:
            if hasattr(command, 'name'):
                name = command.name
            else:
                name = type(command).__name__.lower()
                name = re.sub(r'command$', '', name)

        if isinstance(command, Manager):
            command.parent = self

        if isinstance(command, type):
            command = command()

        namespace = kwargs.get('namespace')
        if not namespace:
            namespace = getattr(command, 'namespace', None)

        if namespace:
            if namespace not in self._commands:
                self.add_command(namespace, Manager())
            self._commands[namespace]._commands[name] = command
        else:
            self._commands[name] = command

    def option(self, *args, **kwargs):
        op = Option(*args, **kwargs)
        def wrapper(func):
            name = func.__name__
            if name not in self._commands:
                command = Command()
                command.run = func
                command.__doc__ = func.__doc__
                command.option_list = []
                self.add_command(name, command)

            self._commands[name].options_list.append(op)
            return func
        return wrapper

    def command(self, func):
        command = Command(func)
        self.add_command(func.__name__, command)
        return func

    def add_default_commands(self):
        if "runserver" not in self._commands:
            self.add_command("runserver", RunServerCommand())
        if 'gencommand' not in self._commands:
            self.add_command("gencommand", GenCommand())

    async def _patch_argparser(self, parser):

        async def _parser_known_args(self, arg_strings, *args, **kwargs):
            if not arg_strings:
                self.print_help()
                self.exit(2)

            return self._parse_known_args2(arg_strings, *args, **kwargs)

        parser._parse_known_args2 = parser._parse_known_args
        parser._parse_known_args = MethodType(_parser_known_args, parser)

    async def create_parser(self, prog, func_stack=(), parent=None):
        prog = os.path.basename(prog)
        func_stack += (self, )
        options_parser = argparse.ArgumentParser(add_help=False)
        for options in await self.get_options():
            options_parser.add_argument(*options.args, **options.kwargs)

        parser = argparse.ArgumentParser(prog=prog, usage=self.usage,
                                         description=self.description,
                                         parents=[options_parser],
                                         add_help=False)
        add_help(parser, self.help_args)
        subparsers = parser.add_subparsers(**self.subparser_kwargs)
        for name, command in self._commands.items():
            usage = getattr(command, 'usage', None)
            help = getattr(command, 'help', None)
            if help is None: help = command.__doc__
            description = getattr(command, 'description', None)
            if description is None: description = command.__doc__
            command_parser = await command.create_parser(name, func_stack=func_stack, parent=self)
            subparsers.add_parser(name, usage=usage, help=help,
                                  description=description,
                                  parents=[command_parser],
                                  add_help=False)

        self.parser = parser
        return parser

    async def handle(self, prog, args=None):
        self.add_default_commands()
        app_parser = await self.create_parser(prog)
        args = list(args or [])
        app_namespace, remaining_args = app_parser.parse_known_args(args)
        kwargs = app_namespace.__dict__
        func_stack = kwargs.pop('func_stack', None)
        if not func_stack:
            app_parser.error('too few arguments')

        last_stack = func_stack[-1]
        if remaining_args and not getattr(last_stack, 'capture_all_args', False):
            app_parser.error('too many arguments')

        args = []
        res = None
        for handle in func_stack:
            if handle is func_stack[0]:
                continue
            config_keys = [action.dest for action in handle.parser._actions if handle is last_stack or action.__class__ in safe_actions]
            config = {k: v for k, v in kwargs.items() if k in config_keys}
            kwargs = {k: v for k, v in kwargs.items() if k not in config_keys}
            if handle is last_stack and getattr(last_stack, 'capture_all_args', False):
                args.append(remaining_args)
            try:
                res = await handle(*args, **config)
            except TypeError as err:
                err.args = (f"{handle}: {str(err)}", )
                raise

            args = [res]

        assert not kwargs
        return res

    async def run(self, commands=None, default_command=None):
        async with self:
            if commands:
                self._commands.update(commands)

            argv = [arg for arg in sys.argv]
            if default_command is not None and len(argv) == 1:
                argv.append(default_command)

            try:
                result = await self.handle(argv[0], argv[1:])
            except SystemExit as e:
                result = e.code

            sys.exit(result or 0)

    async def __aenter__(self):
        for handler in self.app.router.on_startup:
            if handler.__name__ == 'init_orm':
                await handler()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for handler in self.app.router.on_shutdown:
            if handler.__name__ == 'close_orm':
                await handler()
