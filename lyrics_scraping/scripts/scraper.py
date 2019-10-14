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
    ``$ scraper [-h] [-s] [-c [{u,p}]] [-e {log,main}] [-a APP] [-r {log,main}]``

Start the lyrics scraper::

    $ scraper -s

Edit the main config file with TextEdit (macOS)::

    $ scraper -e main -a TextEdit

Edit the logging config file with the default application (e.g. atom)::

    $ scraper -e log

Reset the main config file to default values::

    $ scraper -r main

Notes
-----
More information is available at:

- TODO: add PyPi URL
- https://github.com/raul23/LyricsScraping

"""

import argparse
import logging
import os
import platform
import shutil
import sqlite3
import traceback

import pyutils.exceptions
from lyrics_scraping.scrapers.azlyrics_scraper import AZLyricsScraper
from lyrics_scraping.utils import get_data_filepath
from pyutils.genutils import load_yaml, run_cmd
from pyutils.log.logging_wrapper import LoggingWrapper
from pyutils.logutils import setup_logging


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

    Raises
    ------
    FileNotFoundError
        Raised if the command to open the external program fails, e.g. the name
        of the application doesn't refer to an executable.

    """
    # Get path to user-defined config file
    filepath = get_data_filepath(cfg_type)
    # Command to open the config file with the default application on the
    # specific OS or by the user-specified app, e.g. `open file_path` in macOS
    # opens the file with the default app (e.g. atom)
    default_app_dict = {'Darwin': 'open {path}',
                        'Windows': 'cmd /c start "" "{path}"'}
    default_cmd = default_app_dict.get(platform.system(), 'xdg-open {path}')
    # NOTES:
    # - `app is None` implies that the default app will be used
    # - Otherwise, the user-specified app will be used
    cmd = default_cmd if app is None else app + " " + filepath
    retcode = None
    try:
        # IMPORTANT: if the user provided the name of an app, it will be used as
        # a command along with the file path, e.g. `$ atom {filepath}`. However,
        # this case might not work if the user provided an app name that doesn't
        # refer to an executable, e.g. `$ TextEdit {filepath}` won't work. The
        # failed case is further processed in the `except FileNotFoundError`.
        retcode = run_cmd(cmd.format(path=filepath))
    except FileNotFoundError as e:
        # This happens if the name of the app can't be called as an executable
        # on the terminal
        # e.g. TextEdit can't be run on the terminal but atom can since it
        # refers to an executable (script/atom).
        # To open TextEdit from the terminal, the command `open -a {app_name}`
        # must be used on macOS.
        if platform.system() == 'Darwin':
            # Get the command to open the file with the user-specified app
            # TODO: add the open commands for the other OSes
            specific_app_dict = {'Darwin': 'open -a {app}'.format(app=app)}
            cmd = specific_app_dict.get(platform.system(), app) + " " + filepath
            retcode = run_cmd(cmd)
        raise
    finally:
        if retcode == 0:
            print("Opening the {} configuration file ...".format(cfg_type))
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
    # Get the paths to the default and user-defined config files
    default_cfg_filepath = get_data_filepath(
        file_type='default_s{}'.format(cfg_type))
    user_cfg_filepath = get_data_filepath(file_type=cfg_type)
    # TODO: use shutils.copyfile
    try:
        shutil.copyfile(default_cfg_filepath, user_cfg_filepath)
    except OSError as e:
        print(e)
        return 1
    else:
        print("The {} configuration file is reset".format(cfg_type))
        return 0


def start_scraper(color_logs=None):
    """Start the lyrics scraper.

    The lyrics scraper is setup based on the main configuration file
    *main_cfg.yaml* which can be edited with the command::

        $ scraper -e {log,main}

    Parameters
    ----------
    color_logs : None, optional
        Whether to add color to logs (the default value is False which implies
        that no color will be added to log messages).

    Returns
    -------

    """
    status_code = 1
    # Get the filepaths to the user-defined main and logging config files
    main_cfg_filepath = get_data_filepath(file_type='main')
    log_cfg_filepath = get_data_filepath(file_type='log')
    # Load the main config dict from the config file on disk
    main_cfg = load_yaml(main_cfg_filepath)
    # Setup logging if required
    if main_cfg['use_logging']:
        # Setup logging from the logging config file: this will setup the
        # logging to all custom modules, including the current script
        setup_logging(log_cfg_filepath)
    logger = logging.getLogger('scripts.scraper')
    try:
        # Experimental option: add color to log messages
        if color_logs is not None:
            os.environ['COLOR_LOGS'] = color_logs
            logger = LoggingWrapper(logger, color_logs)
            # We need to wrap the db_utils's logger with LoggingWrapper which
            # will add color to log messages.
            from pyutils import dbutils
            dbutils.logger = LoggingWrapper(dbutils.logger, color_logs)
            logger.debug("The log messages will be colored"
                         " ('{}')".format(color_logs))
        logger.info("Main config file loaded")
        logger.info("Logging is setup")
        # Start the scraping of lyrics webpages
        logger.info("Starting the lyrics scraping")
        scraper = AZLyricsScraper(**main_cfg)
        scraper.start_scraping()
    except (FileNotFoundError, KeyboardInterrupt, KeyError, OSError,
            sqlite3.Error, pyutils.exceptions.LoggingSanityCheckError) as e:
        logger.exception(e)
    else:
        # Success
        status_code = 0
    finally:
        if status_code == 1:
            # Error
            logger.warning("Program will exit")
        else:
            logger.info("End of the lyrics scraping")
        # ipdb.set_trace()
        return status_code


def setup_arg_parser():
    """Setup the argument parser for the command-line script.

    Related arguments are grouped according to the three types of actions that
    can be performed with the script:

    - start the lyrics scraper,
    - edit a configuration file or
    - reset a configuration file.

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
    # Setup the parser
    parser = argparse.ArgumentParser(
        description="Scrape lyrics from webpages and save them locally in a "
                    "SQLite database or a dictionary. Also, you can edit or "
                    "reset a configuration file which can either be the "
                    "logging or the main config file.")
    # Group arguments that are closely related
    start_group = parser.add_argument_group('Start the lyrics scraping')
    start_group.add_argument(
        "-s", "--start_scraping",
        action="store_true",
        help="Scrape lyrics from webpages and save them locally in a SQLite "
             "database or a dictionary")
    start_group.add_argument(
        "-c", "--color_logs",
        const="u",
        nargs='?',
        default=None,
        choices=["u", "p"],
        help="Add colors to log messages. By default, we use colors as"
             " defined for the standard Unix Terminal ('u'). If working with"
             " the PyCharm terminal, use the value 'p' to get better"
             " colors suited for this type of terminal.")
    edit_group = parser.add_argument_group('Edit a configuration file')
    edit_group.add_argument(
        "-e", "--edit",
        choices=["log", "main"],
        help="Edit a configuration file. Provide 'log' (without the quotes) "
             "for the logging config file or 'main' (without the quotes) for "
             "the main config file.")
    edit_group.add_argument("-a",
                            "--app_name",
                            default=None,
                            dest="app",
                            help="Name of the application to use for editing "
                                 "the file. If no name is given, then the "
                                 "default application for opening this type of "
                                 "file will be used.")
    reset_group = parser.add_argument_group('Reset a configuration file')
    reset_group.add_argument(
        "-r", "--reset",
        choices=["log", "main"],
        help="Reset a configuration file with default values. Provide 'log' "
             "(without the quotes) for the logging config file or 'main' "
             "(without the quotes) for the main config file.")
    return parser.parse_args()


def main():
    """Main entry-point to the script.

    According to the user's choice of action, the script will:

    - start the scraper,
    - edit a configuration file, or
    - reset a configuration file.

    """
    args = setup_arg_parser()
    try:
        if args.edit:
            edit_config(args.edit, args.app)
        elif args.reset:
            reset_config(args.reset)
        elif args.start_scraping:
            start_scraper(args.color_logs)
        else:
            # TODO: default when no action given is to start scraping?
            print("No action selected: edit (-e), reset (-r) or start the scraper "
                  "(-s)")
    except (AssertionError, FileNotFoundError):
        traceback.print_exc()


if __name__ == '__main__':
    main()
