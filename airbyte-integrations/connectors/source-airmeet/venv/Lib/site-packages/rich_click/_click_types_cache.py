# This file exists to keep around original copies of all the Click types.
# This is needed for rich_help_rendering, which is lazy-loaded after `rich-click` patching occurs.
# However, this file needs to be instantiated _before_ patching occurs.
from click import Argument as Argument
from click import Command as Command
from click import CommandCollection as CommandCollection
from click import Group as Group
from click import Option as Option
