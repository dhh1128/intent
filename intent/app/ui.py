import types
from rich.console import Console
from rich.style import Style

err_style = Style(color="red", bold=True)
warn_style = Style(color="yellow", bold=True)

ui = Console()

# Monkey patch this object with some extra methods.
def info(self, msg):
    self.print(msg)
def warn(self, msg):
    self.print(msg, style=warn_style)
def err(self, msg):
    self.print(msg, style=err_style)
ui.info = types.MethodType(info, ui)
ui.warn = types.MethodType(warn, ui)
ui.err = types.MethodType(err, ui)

from rich_argparse import RichHelpFormatter as ArgparseFormatter

__all__ = ['ui', 'ArgparseFormatter']	
