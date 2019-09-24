#!/usr/bin/env python
"""Script to scrape lyrics websites, edit and reset a configuration file.

The script scrapes lyrics from webpages and saves them in a dictionary and a
database (if one was initially configured).

The configuration file can either be:
- the main configuration file : used for configuring a lyrics scraper
- the logging configuration file : used to set up the logging for all custom
                                   modules

The configuration file can either be edited by a specific application (e.g.
atom) or if no application is provided, by a default application associated
with this type of file.

The configuration file can also be reset with default values.

Usage
-----
    $ scraper [-h] [-s] [-c [{u,p}]] [-e {log,main}] [-a APP] [-r {log,main}]

Start the lyrics scraper:
    $ scraper -s

Edit the main config file with TextEdit (macOS):
    $ scraper -e main -a TextEdit

Edit the logging config file with the default application (e.g. atom):
    $ scraper -e log

Reset the main config file to default values:
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
import sqlite3
# Custom modules
import pyutils.exceptions.log as log_exc
from lyrics_scraping.scrapers.azlyrics_scraper import AZLyricsScraper
from lyrics_scraping.utils import get_config_filepath
from pyutils.genutils import copy_file, read_yaml, run_cmd
from pyutils.log.logging_wrapper import LoggingWrapper
from pyutils.logutils import setup_logging


def edit_config(args):
    """

    Parameters
    ----------
    args

    Returns
    -------

    """
    app = args.app
    filepath = get_config_filepath(args.edit)
    # Command to open file with default application on the specific OS
    # e.g. `open file_path` in macOS
    default_app_dict = {'Darwin': 'open {path}',
                        'Windows': 'cmd /c start "" "{path}"'}
    default_cmd = default_app_dict.get(platform.system(), 'xdg-open {path}')
    cmd = default_cmd if app is None else app + " " + filepath
    # TODO: add comments
    retcode = None
    try:
        retcode = run_cmd(cmd.format(path=filepath))
    except FileNotFoundError as e:
        # e.g. the app name is not found
        specific_app_dict = {'Darwin': 'open -a {app}'.format(app=app)}
        cmd = specific_app_dict.get(platform.system(), app)
        cmd += " " + filepath
        retcode = run_cmd(cmd)
    finally:
        if retcode:
            # Error
            print("Return code is ", retcode)
        else:
            print("Opening the {} configuration file ...".format(args.edit))
        return retcode


def reset_config(args):
    """

    Parameters
    ----------
    args

    Returns
    -------

    """
    # Add comments
    orig_cfg_filepath = get_config_filepath(cfg_type=args.reset, orig=True)
    user_cfg_filepath = get_config_filepath(cfg_type=args.reset, orig=False)
    try:
        copy_file(source_filepath=orig_cfg_filepath,
                  dest_filepath=user_cfg_filepath)
    except OSError as e:
        print(e)
        return 1
    else:
        print("The {} configuration file is reset".format(args.reset))
        return 0


def start_scraper(args):
    """

    Parameters
    ----------
    args

    Returns
    -------

    """
    status_code = 1
    # Get the filepaths to the main and logging config files
    main_cfg_filepath = get_config_filepath(cfg_type='main', orig=False)
    log_cfg_filepath = get_config_filepath(cfg_type='log', orig=False)
    # Load the main config dict from the config file on disk
    main_cfg = read_yaml(main_cfg_filepath)
    # Setup logging if required
    if main_cfg['use_logging']:
        # Setup logging from the logging config file: this will setup the
        # logging to all custom modules, including the current script
        setup_logging(log_cfg_filepath)
    logger = logging.getLogger('bin.scraper')
    try:
        # Experimental option: add color to log messages
        if args.color_logs is not None:
            os.environ['COLOR_LOGS'] = args.color_logs
            logger = LoggingWrapper(logger, args.color_logs)
            # We need to wrap the db_utils's logger with LoggingWrapper which
            # will add color to log messages.
            from pyutils import dbutils
            dbutils.logger = LoggingWrapper(dbutils.logger, args.color_logs)
            logger.debug("The log messages will be colored"
                         " ('{}')".format(args.color_logs))
        logger.info("Main config file loaded")
        logger.info("Logging is setup")
        # Start the scraping of lyrics webpages
        logger.info("Starting the lyrics scraping")
        scraper = AZLyricsScraper(**main_cfg)
        scraper.start_scraping()
    except (FileNotFoundError, KeyboardInterrupt, KeyError, OSError,
            sqlite3.Error, sqlite3.OperationalError,
            log_exc.LoggingSanityCheckError) as e:
        logger.exception(e)
    else:
        # Success
        status_code = 0
        logger.info("End of the lyrics scraping")
    finally:
        if status_code == 1:
            # Error
            logger.warning("Program will exit")
        # ipdb.set_trace()
        return status_code


def setup_arg_parser():
    """

    Returns
    -------

    """
    # Setup the parser
    parser = argparse.ArgumentParser(
        description="Scrape lyrics from webpages and save them locally in a "
                    "SQLite database or a dictionary. Also, you can edit or "
                    "reset a configuration file which can either be the "
                    "logging or the main config file.")
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
    """

    Returns
    -------

    """
    args = setup_arg_parser()
    if args.edit:
        edit_config(args)
    elif args.reset:
        reset_config(args)
    elif args.start_scraping:
        start_scraper(args)
    else:
        pass


if __name__ == '__main__':
    main()
