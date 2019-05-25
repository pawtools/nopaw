import os
import logging

__all__ = [
    "get_logger",
]

prefixline = '   [block]   '

formatline = lambda l: '\n'.join(
    [prefixline+ls if ls else '' for ls in l.split('\n')] +
    ( [''] if len(l.split('\n'))>1 else [])
    )

def get_logger(logname, loglevel=None, logfile=False):

    # FIXME maybe... this circles on the name
    #       'loglevel' if given as argument
    if loglevel:
        _loglevel = loglevel

    else:
        _loglevel = os.environ.get('PAW_LOGLEVEL',"WARNING")

    # catch attempted set values as WARNING level
    if isinstance(_loglevel, str):
        if _loglevel.lower() == 'info':
            loglevel = logging.INFO

        elif _loglevel.lower() == 'debug':
            loglevel = logging.DEBUG

        elif _loglevel.lower() == 'warning':
            loglevel = logging.WARNING

        elif _loglevel.lower() == 'error':
            loglevel = logging.ERROR

        else:
            print("Could not interpret given loglevel '%s'"%_loglevel)
            print(" --> Setting PAW loglevel to warning")

            loglevel = logging.WARNING

    else:
        print("Invalid loglevel input")
        print(" --> Setting PAW loglevel to warning")

        loglevel = logging.WARNING

    formatter = logging.Formatter(
        '%(asctime)s :: %(name)s :: %(levelname)s || %(message)s'
    )

    logging.basicConfig(level=loglevel)#, format=formatter)
    logger  = logging.getLogger(logname)

    ch = logging.StreamHandler()
    #ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(loglevel)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    if logfile:

        logfilename = 'nopaw'

        if isinstance(logfile, str):
            logfilename = logfile

        logfile = logfilename + '.' + logname + '.log'

        fh = logging.FileHandler(logfile)
        fh.setLevel(loglevel)
        fh.setFormatter(formatter)

        logger.addHandler(fh)

    logger.propagate = False

    return logger
