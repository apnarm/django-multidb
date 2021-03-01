# -*- coding: utf-8 -*-

colorize_enabled = True

_tc = {
    'black': '\033[90m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'purple': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'end': '\033[0m',
}
_tc_end = _tc['end']

def colorize(message, color):
    return ''.join((_tc[color], message, _tc_end)) if colorize_enabled else message
