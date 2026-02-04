# commands/__init__.py

# 1. Import the registry so it's accessible as commands.COMMAND_MAP
from .base import COMMAND_MAP, register_command

# 2. Import every file where you wrote commands. 
# This "wakes up" the decorators in those files.
from . import military
from . import economy
from . import misc
# (add more imports here as you create more command files)

# Now, any other file can just do 'from commands import COMMAND_MAP'