"""Module that defines tests for :mod:`~lyrics_scraping.scripts.scraping`

The script ``scraping.py`` is tested here with different combinations of
command-line options.

"""

from .utils import TestLyricsScraping
from lyrics_scraping.scripts import scraping
from pyutils.genutils import get_qualname


class TestScrapingScript(TestLyricsScraping):
    # TODO
    TEST_MODULE_NAME = get_qualname(scraping)
    LOGGER_NAME = __name__
    SHOW_FIRST_CHARS_IN_LOG = 0

    # @unittest.skip("test_edit_config()")
    def test_edit_config(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>edit_config()</color>...")

    # @unittest.skip("test_reset_config()")
    def test_reset_config(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>reset_config()</color>...")

    # @unittest.skip("test_start_scraper()")
    def test_start_scraper(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>start_scraper()</color>...")

    # @unittest.skip("setup_arg_parser()")
    def test_setup_arg_parser(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>setup_arg_parser()</color>...")

    # @unittest.skip("test_main()")
    def test_main(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>main()</color>...")
