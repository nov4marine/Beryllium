# commands/base.py
COMMAND_MAP = {}

def register_command(name):
    def wrapper(cls):
        COMMAND_MAP[name] = cls
        return cls
    return wrapper