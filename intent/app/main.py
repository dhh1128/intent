import argparse
import sys

from ..version import __version__
from ..lang.parts.space import Space
from .ui import ui, ArgparseFormatter

__all__ = ['main']

class CmdlineSyntaxError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

def compile(args):
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
    Space.init(args.where)

def help(args):
    syntax: argparse.ArgumentParser = globals().get(args.command + '_syntax')
    if not syntax:
            raise CmdlineSyntaxError(f'Unrecognized command "{args.command}".')
    syntax.print_help()

syntax = argparse.ArgumentParser(prog='i', description="Work with intent code.", add_help=False, formatter_class=ArgparseFormatter)
syntax.add_argument('-h', '--help', '--H', '-?', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
syntax.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode.')
commands = syntax.add_subparsers(dest='func', required=True, help="Commands")

compile_syntax = commands.add_parser('compile', help="Compile code.")
compile_syntax.add_argument('what', type=str, metavar='WHAT', nargs='*', help="space, package, or module")

init_syntax = commands.add_parser('init', help="Init a space, or plug gaps in partly inited space.")
init_syntax.add_argument('where', default='.', type=str, nargs='?', help="existing folder to init as space")
init_syntax.add_argument('--force', action='store_true', help='Create even when location appears wrong.')

ignore_syntax = commands.add_parser('ignore', help="Modify .iignore.")
#ignore_syntax.add_argument('--count', type=int, default=1, help="Number of times to run.")

help_syntax = commands.add_parser('help', help="Display help on a specific command.")
help_syntax.add_argument('command', type=str, metavar='CMD', nargs='?', help="which command")

def main():
    # First check for --version.
    if '--version' in sys.argv:
        print(__version__)
        return
    
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

    if show_syntax:
        syntax.print_help()

if __name__ == "__main__":
    main()