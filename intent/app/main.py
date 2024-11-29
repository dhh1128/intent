import argparse

# This is the only stuff we want to expose.
__all__ = ['main']

SYNTAX = argparse.ArgumentParser(prog='i', description="Work with intent code.")
CMDS = SYNTAX.add_subparsers(dest='cmd', required=True, help="Commands")

compile_syntax = CMDS.add_parser('compile', help="Compile code.")
compile_syntax.add_argument('what', type=str, nargs='*', help="space, package, or module")

fix_syntax = CMDS.add_parser('fix', help="Fix warnings.")
#fix_syntax.add_argument('--count', type=int, default=1, help="Number of times to run.")
ignore_syntax = CMDS.add_parser('ignore', help="Modify .iignore.")
#ignore_syntax.add_argument('--count', type=int, default=1, help="Number of times to run.")

# Parse the arguments passed to the program
args = SYNTAX.parse_args()

def compile(args):
    print("compiling")

def main():
    func = globals().get(args.cmd)
    if func:
        func(args)
    else:
        SYNTAX.print_help()

if __name__ == "__main__":
    main()