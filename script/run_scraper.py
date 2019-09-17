#!/usr/bin/env python
"""Script for scraping lyrics websites.

The script scrapes lyrics from webpages and saves them in a dictionary and a
database (if one was initially configured).

`main_cfg.yaml <https://bit.ly/2klaf6m/>`_ is the config file for configuring
the script such as the list of URLS to lyrics webpages, the path to the cache
directory where all lyrics webpages are saved, and the path to the SQLite music
database where all the scraped data are saved.

Check the LyricsScraper's class docstring [1] for a detailed explanation of all
the options in the `main_cfg.yaml` config file.

IMPORTANT: Don't confuse the options `overwrite_db` and `update_tables` in
`main_cfg.yaml`:
- `overwrite_db` : this relates to the whole SQLite database file. Thus, if it
                   is True, then the database **file** can be overwritten.
- `update_tables` : this relates to the tables in the database. Thus, if it is
                    True, then the **tables** can be updated.

Notes
-----
In the logging setup, ignore the experimental option that adds color to log
messages by reading the environmental variable `COLOR_LOGS`.

References
----------
.. [1] `lyrics_scraper.py <https://bit.ly/2kK5bbP/>`_.

"""

import argparse
import logging
import os
import sqlite3
import sys
# Custom modules
from scrapers.azlyrics_scraper import AZLyricsScraper
import utils.exceptions.log as log_exc
from utils.genutils import add_default_arguments, read_yaml
from utils.logging.logging_wrapper import LoggingWrapper
from utils.logging.logutils import setup_logging_from_cfg
import ipdb


if __name__ == '__main__':
    # Setup the parser
    parser = argparse.ArgumentParser(
        description="Scrape lyrics from webpages and save them locally in a "
                    "SQLite database or a dictionary.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Add some default arguments to the script
    add_default_arguments(parser)
    args = parser.parse_args()
    status_code = 1
    main_cfg = read_yaml(args.main_cfg)
    if main_cfg['use_logging']:
        # Setup logging from the logging config file: this will setup the
        # logging to all custom modules, including the current script
        setup_logging_from_cfg(args.logging_cfg)
    logger = logging.getLogger('script.run_scraper')
    try:
        # Experimental option: add color to log messages
        os.environ['COLOR_LOGS'] = args.color_logs
        if args.color_logs:
            logger = LoggingWrapper(logger, args.color_logs)
            # We need to wrap the db_utils's logger with LoggingWrapper which
            # will add color to log messages.
            from utils.databases import dbutils
            dbutils.logger = LoggingWrapper(dbutils.logger, args.color_logs)
            logger.debug("The log messages will be colored"
                         " ('{}')".format(args.color_logs))
        logger.info("Main config file loaded")
        logger.info("Logging is setup")
        # Start the scraping of lyrics webpages
        logger.info("Starting the web scraping")
        scraper = AZLyricsScraper(**main_cfg)
        scraper.start_scraping()
    except (FileNotFoundError, KeyboardInterrupt, KeyError, OSError,
            sqlite3.Error, sqlite3.OperationalError,
            log_exc.LoggingWrapperSanityCheckError) as e:
        logger.exception(e)
    else:
        status_code = 0
        logger.info("End of the web scraping")
    finally:
        if status_code == 1:
            logger.warning("Program will exit")
        # ipdb.set_trace()
        sys.exit(status_code)
