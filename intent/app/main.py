import argparse
import sys
from typing import Callable

from ..version import __version__
from ..lang.parts.space import Space
from .ui import ui, ArgparseFormatter

__all__ = ['main']

class CmdlineSyntaxError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

def root(args):
    """Report fq path to root of current space, if it's inited."""
    root = Space.find_root('.')
    if root:
        print(root)

def ignore(args):
    """Ignore a file or folder."""
    print("ignoring")

def compile(args):
    """Compile space, package, or module."""
    for item in args.what:
        if item == "space":
            print("compiling space")
        elif item == "package":
            print("compiling package")
        elif item == "module":
            print("compiling module")
        else:
            print("nothing to compile")

def init(args):
    """Init a space, or plug gaps in partly inited space."""
    Space.init(args.where, force=args.force)

def help(args):
    """Show help for a command."""
    syntax: argparse.ArgumentParser = globals().get(args.command + '_syntax')
    if not syntax:
            raise CmdlineSyntaxError(f'Unrecognized command "{args.command}".')
    syntax.print_help()

syntax = argparse.ArgumentParser(prog='i', description="Work with intent code.", add_help=False, formatter_class=ArgparseFormatter)
syntax.add_argument('-h', '--help', '--H', '-?', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
syntax.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode.')
commands = syntax.add_subparsers(dest='func', required=True, help="Commands")

def child(commands, func: Callable):
    return commands.add_parser(func.__name__, help=func.__doc__, formatter_class=ArgparseFormatter, add_help=False)

compile_syntax = child(commands, compile) #-----------------------------------
compile_syntax.add_argument('what', type=str, metavar='WHAT', nargs='*', help="space, package, or module")

init_syntax = child(commands, init) #-----------------------------------------
init_syntax.add_argument('where', default='.', metavar='PATH', type=str, nargs='?', help="existing folder to init as space")
init_syntax.add_argument('--force', action='store_true', help='Create even when location appears wrong.')

root_syntax = child(commands, root) #-----------------------------------------
root_syntax.add_argument('where', default='.', metavar='PATH', type=str, nargs='?', help="file or folder inside the space")

ignore_syntax = child(commands, ignore) #-------------------------------------

help_syntax = child(commands, help) #-----------------------------------------
help_syntax.add_argument('command', type=str, metavar='CMD', nargs='?', help="which command")

def main():
    # First check for --version.
    if '--version' in sys.argv:
        print(__version__)
        return
    
    show_syntax = False
    # Treat "i help" as a special case synonym for i --help.
    if len(sys.argv) == 2 and sys.argv[1] == 'help':
        show_syntax = True
    else:        
        # Parse the normal arguments passed to the program.
        args = syntax.parse_args()

        show_syntax = False
        func = globals().get(args.func)
        try:
            if func:
                func(args)
            else:
                raise CmdlineSyntaxError(f'Unrecognized command "{args.func}".')
        except CmdlineSyntaxError as e:
            ui.err(e)
            show_syntax = True
        except Exception as e:
            ui.err(e)

    if show_syntax:
        print()
        syntax.print_help()

if __name__ == "__main__":
    main()