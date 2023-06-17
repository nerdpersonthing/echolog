import os
import re
import inspect
import logging
from datetime import datetime

try:
    # REQUIRED (might make optional at some point) dependency: dotmap
    # nice dict wrapper class that allows calling entries as attributes OR keys
    # e.g. DotMap.entry is equivalent to DotMap['entry']
    from dotmap import DotMap

except ModuleNotFoundError:
    raise ModuleNotFoundError("DotMap module not installed")

    # if/when I make this optional (will require some rewriting),
    # all instances *WILL use dict-style definitions, 
    # so if DotMap is not installed, we can just pass the user dicts instead
    DotMap = dict
    

if os.name == 'nt': # if on Windows
    try: 
        # optional dependency: ansicon
        # enables colored output for Windows cmd console
        import ansicon
        ansicon.load()
    
    except ModuleNotFoundError:
        # if user doesn't have it installed, color won't show properly in the Windows console
        # not a big deal, and it will still work in most other terminals
        pass

# constants
ECHO_LEVEL = logging.DEBUG + 5
__ANSI_ESC = '\033[' # could also be defined as '\x1b['
__ANSI_COLORS = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'gray']
__ANSI_COLORS_ABBV = ['k', 'r',  'g',     'y',      'b',    'm',       'c',    'w',     'gy']

# dictionary of ANSI color codes
C = DotMap()
for i, c in enumerate(__ANSI_COLORS):
    C[c] = C[__ANSI_COLORS_ABBV[i]] = f'{__ANSI_ESC}3{i};1m'
    C['bg_'+c] = C['bg_'+__ANSI_COLORS_ABBV[i]] = f'{__ANSI_ESC}4{i};1m'
C['reset'] = f"{__ANSI_ESC}0m"


def echo(*args, **kwargs):
    """
    A printing function intended largely for debugging. 
    For all passed args/kwargs, it prints both the expression passed to it (in plaintext, as written in the IDE)
    and the value that expression/variable evaluates to.
    """
    
    log = get_logger()
    
    frame = inspect.currentframe().f_back
    frameinfo = inspect.getframeinfo(frame)
    
    line = frameinfo.code_context[0]
    lineno = frameinfo.lineno
    fpath = frameinfo.filename
    _, fname = os.path.split(fpath)

    fmtstr = f"{fname} @ line {C.y}{lineno}{C.reset}:"

    r = re.search(r"\((.*)\)", line).group(1)
    vnames = r.split(", ")
    n_kw = len(kwargs)
    if n_kw > 0:
        vnames = vnames[:n_kw+1]
        for key, value in kwargs.items():
            vnames.append(key)
            args = args + (value,)
    for var, val in zip(vnames, args):
        log.echo(f"{fmtstr} \t {C.c}{var}{C.reset} => {C.g}{val}{C.reset}")

def get_logger(level=None, fmt=None, id=None):
    """
    Sets up a custom logger.
    
    Parameters
    ----------
    level : int or str or None
        Logging level.
        default: logging.ECHO
    fmt : str
        One of the following strings:
        'short', 'short-time', 'long', 'long-time'
        default: short-time
    id : str or None
        ID to use to identify the new logger. If None, it instead modifies the logging module's root logger.
        default: None
        
    Returns
    -------
    logger : logging.Logger
        The created logger (or root logger, if id=None).
    """
    logger = logging.getLogger(id)
    # if args were passed, user clearly wants to overwrite the current config, so flush handlers
    if (level is not None) or (fmt is not None):
        
        for h in logger.handlers:
            h.flush()
        logger.handlers.clear()
    
    # if logger has handlers, then it has been set up and should stay
    if logger.hasHandlers():
        return logger
    else: # overwrite any current loggers
        __get_echo_level()
        
        # defaults if none were passed
        if level == None:
            level = logging.ECHO
        if fmt == None:
            fmt='short-time'
        
        # logging tags for formatting
        tags = DotMap()
        
        tags.short.DEBUG       = "/"
        tags.short.INFO        = "-"
        tags.short.ECHO        = ">"
        tags.short.WARNING     = "!"
        # tags.short.NOTIF     = "o"
        tags.short.ERROR       = "x"
        tags.short.CRITICAL    = "X"
        tags.short.NOTSET      = "?"
        
        tags.long.DEBUG        = "DEBUG"
        tags.long.INFO         = "INFO"
        tags.long.ECHO         = "ECHO"
        tags.long.WARNING      = "WARN"
        # tags.short.NOTIF     = "NOTIF"
        tags.long.ERROR        = "ERROR"
        tags.long.CRITICAL     = "FATAL"
        tags.long.NOTSET       = "UNSET"
        
        # utility dict
        values = DotMap()
        
        values.DEBUG           = logging.DEBUG
        values.INFO            = logging.INFO
        values.ECHO            = logging.ECHO
        values.WARNING         = logging.WARNING
        # values.NOTIF         = logging.NOTIF
        values.ERROR           = logging.ERROR
        values.CRITICAL        = logging.CRITICAL
        values.NOTSET          = logging.NOTSET
        
        # set up formatting strings
        if fmt in ['short', 'short-time']:
            __rename_logging_level_names(tags.short, values)
            
            if fmt == 'short':
                fmt_str = f"[%(levelname)s]"
            else: # fmt == 'short-time'
                fmt_str = f"%(asctime)s.%(msecs)3d [%(levelname)s]"
        
        elif fmt in ['long', 'long-time']:
            
            if fmt == 'long':
                fmt_str = f"%(levelname)s]"
                for lvl, tag in tags.long.items():
                    tags.long[lvl] = '[' + tag
                    if len(tag) == 4:
                        tags.long[lvl] = ' ' + tags.long[lvl]
            else: # fmt == 'long-time'
                fmt_str = f"[%(asctime)s.%(msecs)3d %(levelname)s]"
                for lvl, tag in tags.long.items():
                    if len(tag) == 4:
                        tags.long[lvl] = ' ' + tag
    
            __rename_logging_level_names(tags.long, values)
            
        else:
            raise ValueError(f"Invalid format string: {fmt}.")
        
        # create logger
        formatter = __CustomFormatter(fmt_str)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.setLevel(level)
        logger.addHandler(ch)
        
        # return it
        return logger


def newline(n=1):
    """
    Prints n newlines, if and only if the current logging level is lower than logging.INFO.

    Parameters
    ----------
    n : int
        Number of newlines to print.
        default: 1

    Returns
    -------
        None
    """
    log = get_logger()
    if log.level <= logging.INFO:
        print(''.join(('\n',)*(n-1)))

# custom formatter to support color formatting and etc
class __CustomFormatter(logging.Formatter):
    
    def __init__(self, fmt_str):
        self.fmt_str = fmt_str
        self.FORMATS = {
            logging.DEBUG        : C.b    + fmt_str + C.reset + f' %(message)s',
            logging.INFO         : C.g    + fmt_str + C.reset + f' %(message)s',
            logging.ECHO         : C.m    + fmt_str + C.reset + f' %(message)s',
            logging.WARNING      : C.y    + fmt_str + C.reset + f' %(message)s',
            logging.ERROR        : C.r    + fmt_str + C.reset + f' %(message)s',
            logging.CRITICAL     : C.bg_r + fmt_str + C.reset + f' %(message)s',
            logging.NOTSET       : C.gy   + fmt_str + C.reset + f' %(message)s',
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, r"%H:%M:%S")
        return formatter.format(record)

def __get_echo_level():
    if not hasattr(logging, 'ECHO'):
        __add_logging_level('ECHO', ECHO_LEVEL)
    return logging.ECHO

def __curr_time_str():
    return datetime.now().strftime(format='%H:%M:%S')

def __rename_logging_level_names(tags, vals):
    for level in list(logging._levelToName):
        
        name = None
        for key, val in vals.items():
            if val == level:
                name = tags[key]
        if name == None:
            name = logging.getLevelName(level)
        
        logging.addLevelName(level, name)
    return

def __add_logging_level(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    addLoggingLevel('TRACE', logging.DEBUG - 5)
    logging.getLogger(__name__).setLevel("TRACE")
    logging.getLogger(__name__).trace('that worked')
    logging.trace('so did this')
    logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


if __name__ == "__main__":
    
    # runs a short demo if this file is called directly
    
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



# def dprint(*args):
#     # Old debug printing function.
#     # Uses dark magic (?) to print both name and value of passed arguments.
#     frame = inspect.currentframe().f_back
#     s = inspect.getframeinfo(frame).code_context[0]
#     r = re.search(r"\((.*)\)", s).group(1)
#     vnames = r.split(", ")
#     for i,(var,val) in enumerate(zip(vnames, args)):
#         print(f"{var} = {val}")