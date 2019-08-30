"""Script summary

Extended summary

"""

import argparse
import os
import sqlite3
import sys
# Third-party modules
import ipdb
# Custom modules
from scrapers.azlyrics_scraper import AZLyricsScraper
from utilities.databases.dbutils import create_db
from utilities.exceptions.sql import EmptyQueryResultSetError
from utilities.genutils import read_yaml
from utilities.script_boilerplate import ScriptBoilerplate


if __name__ == '__main__':
    sb = ScriptBoilerplate(
        module_name=__name__,
        module_file=__file__,
        cwd=os.getcwd(),
        parser_desc="Scrape lyrics from webpages and saved them locally in a "
                    "database",
        parser_formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    """
    # Add other arguments
    sb.add_argument(*("-o",),
                    **{"action": "store_true",
                       "dest": "overwrite",
                       "default": False,
                       "help": "Overwrite the database file"})
    sb.add_argument(*("-d", "--database",),
                    **{"default": "database.sqlite",
                       "help": "Path to the SQLite database file"})
    sb.add_argument(*("-s", "--schema",),
                    **{"required": True,
                       "help": "Path to the schema file"})
    """
    sb.parse_args()
    logger = sb.get_logger()
    status_code = 1
    try:
        logger.info("Loading the config file '{}'".format(sb.args.main_cfg))
        main_cfg = read_yaml(sb.args.main_cfg)
        logger.info("Config file loaded!")
        # Create database
        create_db(main_cfg['overwrite_db'],
                  os.path.expanduser(main_cfg['music_db_filepath']),
                  os.path.expanduser(main_cfg['music_schema_filepath']),
                  sb.logging_cfg_dict)
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
