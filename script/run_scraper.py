"""Experimental script for scraping lyrics websites.

IMPORTANT: this is an **experimental** script where I am testing with a new
option for adding color to log messages through the ``LoggingWrapper`` class.

The script scrapes lyrics from webpages and saves them in a dictionary and a
database (if one was initially configured).

`main_cfg.yaml <https://bit.ly/2klaf6m/>`_ is the config file for configuring
the script such as the list of URLS to lyrics webpages, the path to the cache
directory where all lyrics webpages are saved, and the path to the SQLite music
database where all the scraped data are saved.

IMPORTANT: Don't confuse the options `overwrite_db` and `update_tables` in
`main_cfg.yaml`:
* `overwrite_db` : this relates to the whole SQLite database file. Thus, if it
                   is True, then the database **file** can be overwritten.
* `update_tables` : this relates to the tables in the database. Thus, if it is
                    True, then the **tables** can be updated.

"""

import argparse
import logging
import os
import sqlite3
import sys
# Custom modules
from scrapers.azlyrics_scraper import AZLyricsScraper
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
    # Add some default arguments to the script:
    add_default_arguments(parser)
    args = parser.parse_args()
    # Setup logging from the logging config file
    setup_logging_from_cfg(args.logging_cfg, args.add_datetime)
    logger = logging.getLogger('script.run_scraper')
    # Experimental option: add color to log messages
    os.environ['COLOR_LOGS'] = args.color_logs
    if args.color_logs:
        logger = LoggingWrapper(logger, args.color_logs)
        # Setup logging also for the `db_utils` module
        # TODO: explain why the logging setup should be done here [Hint: the
        # module is only functions and we want to add color to log msgs]
        from utils.databases import dbutils
        dbutils.logger = LoggingWrapper(dbutils.logger, args.color_logs)
        logger.debug("The log messages will be colored ('{}')".format(args.color_logs))
    status_code = 1
    try:
        logger.info("Loading the main config file '{}'".format(args.main_cfg))
        main_cfg = read_yaml(args.main_cfg)
        logger.info("Config file loaded!")
        # Start the scraping of lyrics webpages
        logger.info("Starting the web scraping")
        scraper = AZLyricsScraper(**main_cfg)
        scraper.start_scraping()
    except (FileNotFoundError, KeyboardInterrupt, KeyError, OSError,
            sqlite3.Error, sqlite3.OperationalError) as e:
        logger.exception(e)
        logger.warning("Program will exit")
    else:
        status_code = 0
        logger.info("End of the web scraping")
    finally:
        # ipdb.set_trace()
        sys.exit(status_code)
