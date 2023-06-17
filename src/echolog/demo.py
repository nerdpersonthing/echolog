# Runs a short demo.

import logging
from echolog import echo, get_logger, newline

newline(3)

for fmt in ['short-time', 'short', 'long-time', 'long']:
    log = get_logger(level=logging.DEBUG, fmt=fmt)

    echo(       f"Demo echo() call with   fmt={fmt}")
    log.debug(  f'Demo debug message with fmt = {fmt}.')
    log.debug(  f'Demo debug message with fmt = {fmt}.')
    log.echo(   f'Demo echo message with  fmt = {fmt}.')
    log.info(   f'Demo info message with  fmt = {fmt}.')
    log.warning(f'Demo warn message with  fmt = {fmt}.')
    log.error(  f'Demo error message with fmt = {fmt}.')
    log.fatal(  f'Demo fatal message with fmt = {fmt}.')

    newline()

a = 2
b = [3, 4]

echo('Example call to echo() with multiple arguments.', a, blah=b)
newline()
