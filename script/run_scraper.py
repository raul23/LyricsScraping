"""Script summary

Extended summary

"""

import argparse
import os
import sqlite3
import sys
# Third-party modules
# Custom modules
from scrapers.azlyrics_scraper import AZLyricsScraper
from utilities.exceptions.sql import EmptyQueryResultSetError
from utilities.genutils import read_yaml
from utilities.script_boilerplate import ScriptBoilerplate


if __name__ == '__main__':
    sb = ScriptBoilerplate(
        module_name=__name__,
        module_file=__file__,
        cwd=os.getcwd(),
        parser_desc="Web scrape lyrics and saved them locally",
        parser_formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    sb.parse_args()
    logger = sb.get_logger()
    status_code = 1
    try:
        logger.info("Loading the config file '{}'".format(sb.args.main_cfg))
        main_cfg = read_yaml(sb.args.main_cfg)
        logger.info("Config file loaded!")
        # Start the scraping of job posts
        logger.info("Starting the web scraping")
        AZLyricsScraper(main_cfg=main_cfg,
                        logger=sb.logging_cfg_dict).start_scraping()
    except (FileNotFoundError, KeyboardInterrupt, OSError, sqlite3.Error,
            sqlite3.OperationalError, EmptyQueryResultSetError) as e:
        logger.exception(e)
        logger.warning("Program will exit")
    else:
        status_code = 0
        logger.info("End of the web scraping")
    sys.exit(status_code)
