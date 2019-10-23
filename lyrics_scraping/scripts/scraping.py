#!/usr/script/env python
"""Script to scrape lyrics webpages, edit and reset a configuration file.

The script scrapes lyrics from webpages and saves them in a dictionary and a
database (if one was initially configured).

The configuration file can either be:

- the main configuration file: used for configuring a lyrics scraper
- the logging configuration file: used to set up the logging for all custom \
modules

The configuration file can either be edited by a specific application (e.g.
atom) or if no application is provided, by a default application associated
with this type of file.

The configuration file can also be reset with default values.

Usage
-----
    ``$ scraping [-h] [-s] [-c [{u,p}]] [-e {log,main}] [-a APP] [-r {log,main}]``

Start the lyrics scraper::

    $ scraping -s

Edit the main config file with TextEdit (macOS)::

    $ scraping -e main -a TextEdit

Edit the logging config file with the default application (e.g. atom)::

    $ scraping -e log

Reset the main config file to default values::

    $ scraping -r main

Notes
-----
More information is available at:

- TODO: add PyPi URL
- https://github.com/raul23/LyricsScraping

"""
# TODO: update docstring

import argparse
import logging
import os
import platform
import shutil
import sqlite3
from logging import NullHandler

from lyrics_scraping import __version__
from lyrics_scraping.scrapers.azlyrics_scraper import AZLyricsScraper
from lyrics_scraping.utils import get_bak_cfg_filepath, get_data_filepath, load_cfg
from pyutils import uninstall_colored_logger
from pyutils.genutils import load_yaml, run_cmd
from pyutils.logutils import setup_basic_logger, setup_logging_from_cfg

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


# TODO: explain
_TESTING = False


def edit_config(cfg_type, app=None):
    """Edit a configuration file.

    The user chooses what type of config file (`cfg_type`) to edit: 'log' for
    the logging file and 'main' for the main config file.

    The configuration file can be opened by a user-specified application (`app`)
    or a default program associated with this type of file (when `app` is None).

    Parameters
    ----------
    cfg_type : str, {'log', 'main'}
        The type of configuration file we want to edit. 'log' refers to the
        logging config file, and 'main' to the main config file used to setup a
        lyrics scraper.
    app : str
        Name of the application to use to open the config file, e.g. TextEdit
        (the default value is None which implies that the default application
        will be used to open the config file).

    Returns
    -------
    retcode : int
        If there is a `subprocess
        <https://docs.python.org/3/library/subprocess.html#subprocess.CalledProcessError>`_
        -related error, the return code is non-zero. Otherwise, it is 0 if the
        file could be successfully opened with an external program.

    """
    # Get path to user-defined config file
    filepath = get_data_filepath(cfg_type)
    # Command to open the config file with the default application in the
    # OS or the user-specified app, e.g. `open filepath` in macOS opens the
    # file with the default app (e.g. atom)
    default_app_dict = {'Darwin': 'open {filepath}',
                        'Linux': 'xdg-open {filepath}',
                        'Windows': 'cmd /c start "" "{filepath}"'}
    # NOTE: check https://bit.ly/31htaOT (pymotw) for output from
    # platform.system on three OSes
    default_cmd = default_app_dict.get(platform.system())
    # NOTES:
    # - `app is None` implies that the default app will be used
    # - Otherwise, the user-specified app will be used
    cmd = default_cmd if app is None else app + " " + filepath
    retcode = 1
    result = None
    try:
        # IMPORTANT: if the user provided the name of an app, it will be used as
        # a command along with the file path, e.g. `$ atom {filepath}`. However,
        # this case might not work if the user provided an app name that doesn't
        # refer to an executable, e.g. `$ TextEdit {filepath}` won't work. The
        # failed case is further processed in `except FileNotFoundError`.
        result = run_cmd(cmd.format(filepath=filepath))
        retcode = result.returncode
    except FileNotFoundError:
        # This happens if the name of the app can't be called as an executable
        # on the terminal
        # e.g. TextEdit can't be run on the terminal but atom can since the
        # latter refers to an executable.
        # To open TextEdit from the terminal, the command `open -a {app_name}`
        # must be used on macOS.
        if platform.system() == 'Darwin':
            # Get the command to open the file with the user-specified app
            # TODO: add the open commands for the other OSes
            specific_app_dict = {'Darwin': 'open -a {app}'.format(app=app)}
            cmd = specific_app_dict.get(platform.system(), app) + " " + filepath
            # TODO: explain DEVNULL, suppress stderr since we will display the
            # error
            result = run_cmd(cmd)  # stderr=subprocess.DEVNULL)
            retcode = result.returncode
    if retcode == 0:
        logger.info("<color>Opening the {} configuration file ..."
                    "</color>".format(cfg_type))
    else:
        if result:
            err = "<color>{}</color>".format(result.stderr.decode().strip())
            logger.error(err)
    return retcode


def reset_config(cfg_type):
    """Reset a configuration file to its default values.

    The user chooses what type of config file (`cfg_type`) to reset: 'log' for
    the logging file and 'main' for the main config file.

    Parameters
    ----------
    cfg_type : str, {'log', 'main'}
        The type of configuration file we want to reset. 'log' refers to the
        logging config file, and 'main' to the main config file used to setup a
        lyrics scraper.

    Returns
    -------
    retcode: int
        If there is an I/O related error, the return code is 1. Otherwise, it
        is 0 if the config was reset successfully.

    """
    try:
        # TODO: explain
        user_cfg = load_cfg(cfg_type)
        default_cfg = load_cfg('default_' + cfg_type)
        if user_cfg == default_cfg:
            logger.warning("<color>The {} configuration file is already reset"
                           "</color>".format(cfg_type))
            retcode = 2
        else:
            # Get the paths to the default and user-defined config files
            default_cfg_filepath = get_data_filepath('default_' + cfg_type)
            user_cfg_filepath = get_data_filepath(cfg_type)
            # Backup config file (for undo purposes)
            shutil.copyfile(user_cfg_filepath, get_bak_cfg_filepath(cfg_type))
            # Reset config file to factory default values
            shutil.copyfile(default_cfg_filepath, user_cfg_filepath)
            logger.info("<color>The {} configuration file is reset"
                        "</color>".format(cfg_type))
            retcode = 0
    except OSError as e:
        raise e
    else:
        return retcode


def undo_config(cfg_type):
    """TODO

    Parameters
    ----------
    cfg_type

    Returns
    -------

    """
    try:
        if os.path.isfile(get_bak_cfg_filepath(cfg_type)):
            # Undo config file
            shutil.copyfile(get_bak_cfg_filepath(cfg_type),
                            get_data_filepath(cfg_type))
            logger.info("<color>The {} config file was SUCCESSFULLY reverted "
                        "to what it was before the last RESET"
                        "</color>".format(cfg_type))
            # Delete the backup file
            os.unlink(get_bak_cfg_filepath(cfg_type))
            retcode = 0
        else:
            logger.warning("<color>The last RESET was already undo</color>")
            retcode = 2
    except OSError:
        raise
    else:
        return retcode


def start_scraper():
    """Start the lyrics scraper.

    The lyrics scraper is setup based on the main configuration file
    *main_cfg.yaml* which can be edited with the command::

        $ scraper -e {log,main}

    TODO: explain more

    Returns
    -------
    TODO

    """
    status_code = 1
    # Get the filepaths to the user-defined main and logging config files
    main_cfg_filepath = get_data_filepath('main')
    log_cfg_filepath = get_data_filepath('log')
    # Load the main config dict from the config file on disk
    main_cfg = load_yaml(main_cfg_filepath)
    # Setup logging if required
    if main_cfg['use_logging']:
        # Setup logging from the logging config file: this will setup the
        # logging to all custom modules, including the current script
        setup_logging_from_cfg(log_cfg_filepath)
    try:
        logger.info("Main config file loaded")
        logger.info("Logging is setup")
        # Start the scraping of lyrics webpages
        logger.info("Starting the lyrics scraping")
        scraper = AZLyricsScraper(**main_cfg)
        scraper.start_scraping()
    except (FileNotFoundError, KeyboardInterrupt, KeyError, OSError,
            sqlite3.Error):
        raise
    else:
        # Success
        return 0


def setup_argparser():
    """Setup the argument parser for the command-line script.

    The important actions that can be performed with the script are:

    - start the lyrics scraper,
    - edit a configuration file or
    - reset/undo a configuration file.

    Returns
    -------
    args : argparse.Namespace
        Simple class used by default by `parse_args()` to create an object
        holding attributes and return it [1]_.

    References
    ----------
    .. [1] `argparse.Namespace
       <https://docs.python.org/3.7/library/argparse.html#argparse.Namespace>`_.

    """
    # Help message that is used in various arguments
    common_help = '''Provide 'log' (without the quotes) for the logging config 
    file or 'main' (without the quotes) for the main config file.'''
    # Setup the parser
    parser = argparse.ArgumentParser(
        # usage="%(prog)s [OPTIONS]",
        prog=os.path.basename(__file__).split(".")[0],
        description='''\
Scrape lyrics from webpages and save them locally in a SQLite database. Also, 
you can edit or reset a configuration file which can either be the logging or 
the main config file.\n
IMPORTANT: these are only some of the most important options. Open the main 
config file to have access to the complete list of options, i.e. 
%(prog)s -e main''',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # ===============
    # General options
    # ===============
    parser.add_argument("--version", action='version',
                        version='%(prog)s {}'.format(__version__))
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Enable quiet mode, i.e. nothing will be print.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print various debugging information, e.g. print "
                             "traceback when there is an exception.")
    parser.add_argument("-nc", "--no-color", action="store_true",
                        help="Don't print color codes in output")
    # help=argparse.SUPPRESS)
    # Group arguments that are closely related
    # =============
    # Cache options
    # =============
    cache_group = parser.add_argument_group('Cache options')
    cache_group.add_argument(
        "--cache-dir", dest="dir",
        help='''Location in the filesystem where lyrics_scraping can store 
        downloaded webpages permanently. By default ~/.cache/lyrics_scraping is 
        used.''')
    cache_group.add_argument("--no-cache-dir", action="store_true",
                             help="Disable caching")
    cache_group.add_argument("--clr-cache-dir", action="store_true",
                             help="Delete all cache files")
    # ======================
    # Lyrics Scraper options
    # ======================
    start_group = parser.add_argument_group('Start the lyrics scraper')
    start_group.add_argument(
        "-s", "--start_scraper", action="store_true",
        help='''Scrape lyrics from webpages and save them locally in a SQLite 
        database''')
    # ===========
    # Edit config
    # ===========
    edit_group = parser.add_argument_group('Edit a configuration file')
    edit_group.add_argument(
        "-e", "--edit", choices=["log", "main"],
        help="Edit a configuration file. {}".format(common_help))
    edit_group.add_argument(
        "-a", "--app-name", default=None, dest="app",
        help='''Name of the application to use for editing the file. If no 
        name is given, then the default application for opening this type of 
        file will be used.''')
    # =================
    # Reset/Undo config
    # =================
    reset_group = parser.add_argument_group(
        'Reset or undo a configuration file')
    reset_group.add_argument(
        "-r", "--reset", choices=["log", "main"],
        help='''Reset a configuration file with factory default values. 
        {}'''.format(common_help))
    reset_group.add_argument(
        "-u", "--undo", choices=["log", "main"],
        help='''Undo the LAST RESET. Thus, the config file will be restored 
        to what it was before the LAST reset. {}'''.format(common_help))
    return parser.parse_args()


def main():
    """Main entry-point to the script.

    According to the user's choice of action, the script might:

    - start the scraper,
    - edit a configuration file, or
    - reset/undo a configuration file.

    Notes
    -----
    Only one action at a time can be performed.

    """
    # TODO: explain
    global _TESTING, logger
    args = setup_argparser()
    # ==============
    # Logging config
    # ==============
    # NOTE: if quiet and verbose are both activated, only quiet will have an
    # effect
    if args.quiet:  # Logging disabled
        logger = setup_basic_logger(__name__, remove_all_handlers=True)
        logger.addHandler(NullHandler())
    else:  # Logging enabled
        if args.no_color:  # Color disabled
            uninstall_colored_logger()
        if not _TESTING:
            logger = setup_basic_logger(
                name=__name__,
                add_console_handler=True,
                remove_all_handlers=True)
        if args.verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
    # =======
    # Actions
    # =======
    retcode = 1
    try:
        # NOTE: only one action at a time can be performed
        if args.edit:
            retcode = edit_config(args.edit, args.app)
        elif args.reset:
            retcode = reset_config(args.reset)
        elif args.undo:
            retcode = undo_config(args.undo)
        elif args.start_scraper:
            retcode = start_scraper()
        else:
            # TODO: default when no action given is to start scraping?
            print("No action selected: edit (-e), reset (-r) or start the "
                  "scraper (-s)")
    except (AssertionError, AttributeError, FileNotFoundError,
            KeyboardInterrupt, OSError, sqlite3.Error) as e:
        # TODO: explain this line
        # traceback.print_exc()
        e = "<color>{}</color>".format(e)
        if args.verbose:
            logger.exception(e)
        else:
            logger.error(e)
    finally:
        return retcode


if __name__ == '__main__':
    retcode = main()
    msg = "\nProgram exited with <color>{}</color>".format(retcode)
    if retcode == 1:
        logger.error(msg)
    else:
        logger.debug(msg)
