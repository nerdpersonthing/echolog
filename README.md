# echolog
A logging package that adds an "echo" function to return both the input expression/variable and its results. Also sets up nicely-formatted logging.

## Utilities

(function) ``echo(**args, **kwargs)``

    A printing function intended largely for debugging. 
    For all passed args/kwargs, it prints both the expression passed to it (in plaintext, as written in the IDE)
    and the value that expression/variable evaluates to.

(function) ``get_logger(level=None, fmt=None, id=None)``

    Sets up a custom logger.
    
    Parameters
    ----------
    level : int or str or None
        Logging level.
        default: logging.ECHO
    fmt : str
        One of the following strings, defining the logging format:
        'short', 'short-time', 'long', 'long-time'
        default: short-time
    id : str or None
        ID to use to identify the new logger. If None, it instead modifies the logging module's root logger.
        default: None
        
    Returns
    -------
    logger : logging.Logger
        The created logger (or root logger, if id=None).

(function) ``newline(n=1)``

    Prints n newlines, if and only if the current logging level is lower than logging.INFO.

    Parameters
    ----------
    n : int
        Number of newlines to print.
        default: 1

    Returns
    -------
        None

(dict/DotMap) ``C``

    Dictionary including the ANSI color codes for the following colors:

    ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'gray']

    Abbreviations for the colors also work:
    ['k', 'r', 'g', 'y', 'b', 'm', 'c', 'w', 'gy']

    Adding 'bg_' to the start of any of these will get the background ANSI color.
    
    Finally, 'reset' contains the ANSI code to reset to default formatting.

## Example usage

Running `demo.py` executes the following test case:

``` python
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
```

You should probably run this on your own machine to best demonstrate, as Github does not support color text formatting in README files. Without colors, though, the output should look something like this:
``` 
    17:14:07.923 [>] echolog.py @ line 311:                 f"Demo echo() call with   fmt={fmt}" => Demo echo() call with   fmt=short-time
    17:14:07.937 [/] Demo debug message with fmt = short-time.
    17:14:07.937 [/] Demo debug message with fmt = short-time.
    17:14:07.944 [>] Demo echo message with  fmt = short-time.
    17:14:07.944 [-] Demo info message with  fmt = short-time.
    17:14:07.944 [!] Demo warn message with  fmt = short-time.
    17:14:07.944 [x] Demo error message with fmt = short-time.
    17:14:07.949 [X] Demo fatal message with fmt = short-time.

    [>] echolog.py @ line 311:              f"Demo echo() call with   fmt={fmt}" => Demo echo() call with   fmt=short
    [/] Demo debug message with fmt = short.
    [/] Demo debug message with fmt = short.
    [>] Demo echo message with  fmt = short.
    [-] Demo info message with  fmt = short.
    [!] Demo warn message with  fmt = short.
    [x] Demo error message with fmt = short.
    [X] Demo fatal message with fmt = short.

    [17:14:07.965  ECHO] echolog.py @ line 311:             f"Demo echo() call with   fmt={fmt}" => Demo echo() call with   fmt=long-time
    [17:14:07.973 DEBUG] Demo debug message with fmt = long-time.
    [17:14:07.981 DEBUG] Demo debug message with fmt = long-time.
    [17:14:07.981  ECHO] Demo echo message with  fmt = long-time.
    [17:14:07.981  INFO] Demo info message with  fmt = long-time.
    [17:14:07.981  WARN] Demo warn message with  fmt = long-time.
    [17:14:07.981 ERROR] Demo error message with fmt = long-time.
    [17:14:07.989 FATAL] Demo fatal message with fmt = long-time.

     [ECHO] echolog.py @ line 311:          f"Demo echo() call with   fmt={fmt}" => Demo echo() call with   fmt=long
    [DEBUG] Demo debug message with fmt = long.
    [DEBUG] Demo debug message with fmt = long.
     [ECHO] Demo echo message with  fmt = long.
     [INFO] Demo info message with  fmt = long.
     [WARN] Demo warn message with  fmt = long.
     [ERROR] Demo error message with fmt = long.
    [FATAL] Demo fatal message with fmt = long.

     [ECHO] echolog.py @ line 325:   'Example call to echo() with multiple arguments.' => Example call to echo() with multiple arguments.
     [ECHO] echolog.py @ line 325:   a => 2
     [ECHO] echolog.py @ line 325:   blah => [3, 4]
```