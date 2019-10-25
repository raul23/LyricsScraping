"""Module that defines tests for :mod:`~lyrics_scraping.scrapers.azlyrics_scraper`
"""

import logging
import os
import sqlite3
import unittest
from logging import NullHandler

from .utils import TestLyricsScraping
from lyrics_scraping.scrapers import lyrics_scraper
from lyrics_scraping.scrapers import azlyrics_scraper
from lyrics_scraping.scrapers.azlyrics_scraper import AZLyricsScraper
from lyrics_scraping.utils import load_cfg
from pyutils.genutils import get_qualname
from pyutils.logutils import setup_logging_from_cfg

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class TestScrapingScript(TestLyricsScraping):
    # TODO
    TEST_MODULE_QUALNAME = get_qualname(azlyrics_scraper)
    LOGGER_NAME = __name__
    SHOW_FIRST_CHARS_IN_LOG = 0

    @classmethod
    def setUpClass(cls):
        """TODO
        """
        super().setUpClass()
        # We will take charge of setting logging for lyrics_scraper and cie
        lyrics_scraper._SETUP_LOGGING = False
        # Load logging config
        logging_cfg = load_cfg("log")
        # Disable add_datetime
        logging_cfg['add_datetime'] = False
        # Change console handler's level to DEBUG
        logging_cfg['handlers']['console']['level'] = "DEBUG"
        # Change console handler's formatter to 'console'
        logging_cfg['handlers']['console']['formatter'] = "console"
        # Update file handler's filename our test logger's filename
        logging_cfg['handlers']['file']['filename'] = cls.log_filepath
        # Add file handlers to all loggers
        for log_name, log_attrs in logging_cfg['loggers'].items():
            log_attrs['handlers'].append('file')
        # IMPORTANT: remove the root logger because if we don't our test logger
        # will be setup as the root logger in the logging config file
        del logging_cfg['root']
        # Setup logging for all custom modules based on updated logging config
        # dict
        setup_logging_from_cfg(logging_cfg)

    @unittest.skip("test_get_lyrics_case_1()")
    def test_get_lyrics_case_1(self):
        """Test get_lyrics() TODO: ...
        """
        self.log_test_method_name()

    # @unittest.skip("test_init_case_1()")
    def test_init_case_1(self):
        """Test __init__() with default values as its arguments.

        Case 1 simply tests
        :meth:`~lyrics_scraping.scrapers.AZLyricsScraper.__init__` with default
        values as its arguments, nothing is passed to the constructor.

        Thus, no database will be created and the logging setup is not performed
        since it was already done in :meth:`setUpClass`.

        """
        extra_msg = "Case where <color>__init__()</color> is called without " \
                    "arguments, i.e. <color>default values used</color>"
        self._test_init(extra_msg=extra_msg)
        self.log_signs()
        AZLyricsScraper()
        self.log_signs()
        logger.info("The constructor was successfully called")

    # @unittest.skip("test_init_case_2()")
    def test_init_case_2(self):
        """Test that __init__() can create a SQLite database and connect to it.

        Case 2 tests
        :meth:`~lyrics_scraping.scrapers.AZLyricsScraper.__init__` TODO:...

        """
        extra_msg = "Case where <color>__init__()</color> is called with " \
                    "<color>db_filepath</color>"
        self._test_init(extra_msg=extra_msg)
        db_filepath = os.path.join(self.sandbox_tmpdir, "music.sqlite")
        try:
            self.log_signs()
            AZLyricsScraper(db_filepath=db_filepath)
            self.log_signs()
        except (IOError, sqlite3.OperationalError) as e:
            self.log_signs()
            logger.exception("<color>{}</color>".format(e))
            self.fail("Couldn't connect to the database")
        else:
            logger.info("Connection to the SQLite database could be established")

    @unittest.skip("test_init_case_3()")
    def test_init_case_3(self):
        """Test that __init__() TODO:...

        Case 3 tests
        :meth:`~lyrics_scraping.scrapers.AZLyricsScraper.__init__` ...

        """
        import ipdb
        ipdb.set_trace()
        self.log_test_method_name()
        db_filepath = os.path.join(self.sandbox_tmpdir, "music.sqlite")
        AZLyricsScraper(db_filepath=db_filepath)

    def _test_init(self, extra_msg=None):
        """TODO
        """
        self.log_test_method_name()
        case, cfg_func = self.parse_test_method_name()
        info_msg = "Case <color>{}</color> of testing <color>{}()" \
                   "</color>".format(case, cfg_func)
        info_msg += "\n{}".format(extra_msg) if extra_msg else ""
        logger.info(info_msg)
