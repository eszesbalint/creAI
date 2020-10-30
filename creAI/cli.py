"""Commandline interface module.

This module implements a simple commandline interface with docstrings and 
decorators.

You can create simple commandline applications by subclassing
``CommandlineInterface`` and decorating it's methods with ``command`` and
``default_command``.

Example:
    
    class Foo(CommandlineInterface):
        \"""This is an example application.

        Long description.
        \"""
        def __init__(self):
            super(Foo, self).__init__()

        @command
        def bar(self, a, b):
            \"""Bars two integers.

            Long description.

            Args:
                a (int): Integer to bar
                b (int): The other integer to bar
            \"""
            pass

    Foo().run()

    This will create a commandline interface with a subcommand ``bar`` and
    generates help texts and commandline arguments parsed from the docstrings.
"""

import argparse
from functools import wraps
import re
import docstring_parser
import sys
from builtins import int, str, bool




def command(fun):
    fun.is_command = True
    return fun


def default_command(fun):
    fun.is_command = True
    fun.is_default_command = True
    return fun


class CommandlineInterface(object):
    def __init__(self):
        #Parsing docstring
        self.description = docstring_parser.parse(self.__doc__).short_description
        help_text = self.description \
                    + '\n\n' \
                    + docstring_parser.parse(self.__doc__).long_description
        #Creating argument parsers
        self._parser = argparse.ArgumentParser(description=help_text)
        self._parser.set_defaults(cmd='')
        self._subparsers = self._parser.add_subparsers()
        #Commands to expose to the commandline
        self._cmds = {}

        #Finding commands of the class
        for attr in dir(self):
            obj = getattr(self, attr)
            if callable(obj) and hasattr(obj, 'is_command'):
                if hasattr(obj, 'is_default_command'):
                    self._cmds[''] = obj
                    continue

                if obj.__doc__ is None:
                    raise ValueError('Missing docstring for {}!'.format(obj.__name__))
                
                #Parsing docstring
                doc = docstring_parser.parse( obj.__doc__)
                help_text = doc.short_description + '\n\n' \
                            + doc.long_description

                cmd = obj.__name__.replace('_','-')
                parser = self._subparsers.add_parser(cmd, description=help_text)
                parser.set_defaults(cmd=cmd)
                self._cmds[cmd] = obj

                for arg in doc.params:
                    #Creating arguments based on the docstrings
                    parser.add_argument(
                        '--{}'.format(arg.arg_name.replace('_','-')),
                        action='store',
                        type=getattr(sys.modules[__name__], arg.type_name), 
                        help=arg.description,
                        required=not arg.is_optional
                        )
                        
    def run(self):
        self._args = self._parser.parse_args()
        cmd = self._args.cmd

        kwargs = dict(
                [(k, v) 
                for k, v in vars(self._args).items() 
                if k != 'cmd'
                ]
            )
        self._cmds[cmd](**kwargs)





