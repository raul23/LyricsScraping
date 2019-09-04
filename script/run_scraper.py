"""Script for scraping lyrics websites.

The script scrapes lyrics from webpages and saves them locally in a database.
`main_cfg.yaml` is the config file for configuring the script such as the list
of URLS to lyrics webpages, the path to the cache directory where all lyrics
webpages are saved, and the path to the SQLite music database where all the
scraped data are saved.

IMPORTANT: Don't confuse the options `overwrite_db` and `overwrite_tables` in
`main_cfg.yaml`:
* `overwrite_db` : this relates to the whole SQLite database file. Thus, if it
                   is True, then the **file** can be overwritten.
* `overwrite_tables` : this relates to the tables in the database. Thus, if it
                       is True, then the **tables** can be updated.

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
from utilities.genutils import read_yaml
from utilities.script_boilerplate import ScriptBoilerplate
import utilities.exceptions.log as log_exc
import utilities.exceptions.sql as sql_exc

if __name__ == '__main__':
    # TODO: add temporary and basic console logger before the ``try``?
    sb = ScriptBoilerplate(
        module_name=__name__,
        module_file=__file__,
        cwd=os.getcwd(),
        script_desc="Scrape lyrics from webpages and save them locally in a "
                    "SQLite database",
        parser_formatter_class=argparse.ArgumentDefaultsHelpFormatter)
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
        # Start the scraping of lyrics webpages
        logger.info("Starting the web scraping")
        AZLyricsScraper(main_cfg=main_cfg,
                        logger=sb.logging_cfg_dict).start_scraping()
    except (FileNotFoundError, KeyboardInterrupt, KeyError, OSError,
            sqlite3.Error, sqlite3.OperationalError, log_exc.AddLoggerError,
            sql_exc.EmptyQueryResultSetError) as e:
        logger.exception(e)
        logger.warning("Program will exit")
    else:
        status_code = 0
        logger.info("End of the web scraping")
    sys.exit(status_code)
