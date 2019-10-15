"""Module that defines tests for :mod:`~lyrics_scraping.scripts.scraping`

The script ``scraping.py`` is tested here with different combinations of
command-line options.

"""

import sys
import unittest

from .utils import TestLyricsScraping
from lyrics_scraping.scripts import scraping
from pyutils.genutils import get_module_filename, get_qualname


class TestScrapingScript(TestLyricsScraping):
    # TODO
    TEST_MODULE_QUALNAME = get_qualname(scraping)
    LOGGER_NAME = __name__
    SHOW_FIRST_CHARS_IN_LOG = 0

    # @unittest.skip("test_edit_config_case_1()")
    def test_edit_config_case_1(self):
        """Test that edit_config() opens the default app for editing the log
        config file

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the default app for editing the logging config file.

        For example, the default app as determined by the OS can be TextEdit or
        atom.

        """
        self.log_test_method_name()
        self.logger.info("Testing <color>edit_config()</color>...")
        sys.argv = [get_module_filename(scraping), '-e', 'log']
        retcode = scraping.main()
        msg = "The default app couldn't be open. Return code is " \
              "{}".format(retcode)
        self.assertTrue(retcode == 0, msg)
        self.logger.info("The default app could be opened")

    @unittest.skip("test_reset_config()")
    def test_reset_config(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>reset_config()</color>...")

    @unittest.skip("test_start_scraper()")
    def test_start_scraper(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>start_scraper()</color>...")

    @unittest.skip("setup_arg_parser()")
    def test_setup_arg_parser(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>setup_arg_parser()</color>...")

    @unittest.skip("test_main()")
    def test_main(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>main()</color>...")
