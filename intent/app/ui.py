import types
from rich import print
from rich.console import Console
from rich.style import Style

err_style = Style(color="red", bold=True)
warn_style = Style(color="yellow", bold=True)

ui = Console()

# Monkey patch this object with some extra methods.
def warn(self, msg):
    self.print('[bold yellow]Warning: [/bold yellow]: ' + str(msg))

def err(self, msg):
    self.print('[bold red]Error: [/bold red]: ' + str(msg))

ui.warn = types.MethodType(warn, ui)
ui.err = types.MethodType(err, ui)

from rich_argparse import RichHelpFormatter as ArgparseFormatter

__all__ = ['ui', 'ArgparseFormatter']	
