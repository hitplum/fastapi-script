import argparse
import inspect
from gettext import gettext as _


def add_help(parser, help_args):
    if not help_args:
        return

    parser.add_argument(*help_args,
                        action='help',
                        default=argparse.SUPPRESS,
                        help=_('show this help message and exit'))


class Option(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Group(object):

    def __init__(self, *options, **kwargs):
        self.option_list = options
        self.title = kwargs.pop('title', None)
        self.description = kwargs.pop('description', None)
        self.exclusive = kwargs.pop('exclusive', None)
        self.required = kwargs.pop('required', None)
        if (self.title or self.description) and (self.required or self.exclusive):
            raise TypeError("title and/or description cannot be used with "
                            "required and/or exclusive.")

        super().__init__(**kwargs)

    def get_options(self):
        return self.option_list


class Command(object):

    options_list = ()
    help_args = None

    def __init__(self, func=None):
        if func is None:
            if not self.options_list:
                self.options_list = []
            return

        args, varargs, varkw, defaults, *_ = inspect.getfullargspec(func)
        if inspect.ismethod(func):
            args = args[1:]

        options = []
        defaults = defaults or []
        kwargs = dict(zip(*[reversed(i) for i in (args, defaults)]))
        for arg in args:
            if arg in kwargs:
                default = kwargs[arg]
                if isinstance(default, bool):
                    options.append(Option(f'-{arg[0]}',
                                          f'--{arg}',
                                          action='store_true',
                                          dest=arg,
                                          required=False,
                                          default=default))
                else:
                    options.append(Option(f'-{arg[0]}',
                                          f'--{arg}',
                                          dest=arg,
                                          type=str,
                                          required=False,
                                          default=default))
            else:
                options.append(Option(arg, type=str))

        self.run = func
        self.__doc__ = func.__doc__
        self.options_list = options

    def get_options(self):
        return self.options_list

    async def create_parser(self, *args, **kwargs):
        func_stack = kwargs.pop('func_stack', ())
        parent = kwargs.pop('parent', None)
        parser = argparse.ArgumentParser(*args, add_help=False, **kwargs)
        help_args = self.help_args
        while help_args is None and parent is not None:
            help_args = parent.help_args
            parent = getattr(parent, 'parent', None)

        if help_args:
            add_help(parser, help_args)

        for option in self.get_options():
            if isinstance(option, Group):
                if option.exclusive:
                    group = parser.add_mutually_exclusive_group(required=option.required)
                else:
                    group = parser.add_argument_group(title=option.title,
                                                      description=option.description)

                for opt in option.get_options():
                    group.add_argument(*opt.args, **opt.kwargs)
            else:
                parser.add_argument(*option.args, **option.kwargs)

        parser.set_defaults(func_stack=func_stack + (self, ))
        self.parent = parent
        self.parser = parser
        return parser

    async def __call__(self, *args, **kwargs):
        res = self.run(*args, **kwargs)
        if inspect.iscoroutine(res):
            await res

    async def run(self, *args, **kwargs):
        raise NotImplementedError
