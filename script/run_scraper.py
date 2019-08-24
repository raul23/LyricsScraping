import argparse
import os
import sqlite3
import sys
# Third-party modules
import ipdb
# Own modules
from music_scraper.azlyrics_scraper import LyricsScraper
import utilities.exc as exc
from utilities.genutils import read_yaml_config
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
        main_cfg = read_yaml_config(sb.args.main_cfg)
        logger.info("Config file loaded!")
        # Start the scraping of job posts
        logger.info("Starting the web scraping")
        LyricsScraper(main_cfg=main_cfg,
                      logging_cfg=sb.logging_cfg_dict,
                      logger=logger).start_scraping()
    except (FileNotFoundError, KeyboardInterrupt, OSError, sqlite3.Error,
            sqlite3.OperationalError, exc.EmptyQueryResultSetError) as e:
        logger.exception(e)
        logger.warning("Program will exit")
    else:
        status_code = 0
        logger.info("End of the web scraping")
    sys.exit(status_code)
