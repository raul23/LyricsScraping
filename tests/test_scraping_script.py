"""Module that defines tests for :mod:`~lyrics_scraping.scripts.scraping`

The script ``scraping.py`` is tested here with different combinations of
command-line options.

"""

import argparse
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

    # Skip test if on PROD because we are opening an app to edit a file
    @unittest.skipIf(TestLyricsScraping.env_type == "PROD", "Skip if on PROD")
    def test_edit_config_case_1(self):
        """Test that edit_config() opens the default app for editing the
        logging config file

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the default app for editing the logging config file.

        For example, the default app as determined by the OS can be TextEdit or
        atom.

        """
        self.log_test_method_name()
        self._test_edit_config(case=1, cmd=['-e', 'log'])

    # Skip test if on PROD because we are opening an app to edit a file
    @unittest.skipIf(TestLyricsScraping.env_type == "PROD", "Skip if on PROD")
    def test_edit_config_case_2(self):
        """Test that edit_config() opens the default app for editing the main
        config file

        Case 2 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the default app for editing the main config file.

        For example, the default app as determined by the OS can be TextEdit or
        atom.

        """
        self.log_test_method_name()
        self._test_edit_config(case=2, cmd=['-e', 'main'])

    # Skip test if on PROD because we are opening an app to edit a file
    @unittest.skipIf(TestLyricsScraping.env_type == "PROD", "Skip if on PROD")
    def test_edit_config_case_3(self):
        """Test that edit_config() opens the user-selected app for editing the
        logging config file

        Case 3 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the default app for editing the main config file.

        For example, the app can be TextEdit or atom.

        """
        self.log_test_method_name()
        self._test_edit_config(case=3, cmd=['-e', 'log', '-a', 'TextEdit'])

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

    def _test_edit_config(self, case, cmd):
        """TODO

        Parameters
        ----------
        case
        cmd

        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-e", "--edit", choices=["log", "main"])
        parser.add_argument("-a", "--app_name", default=None, dest="app")
        args = parser.parse_args(cmd)
        info_msg = "Case {} of testing <color>edit_config()</color> with the " \
                   "{} config file".format(case, args.edit)
        if args.app:
            info_msg += " and the app '{}'".format(args.app)
        else:
            info_msg += " and using the default app"
        self.logger.info(info_msg)
        sys.argv = []
        sys.argv = [get_module_filename(scraping)]
        sys.argv.extend(cmd)
        retcode = scraping.main()
        msg = "The default app couldn't be open. Return code is " \
              "{}".format(retcode)
        self.assertTrue(retcode == 0, msg)
        info_msg = "'{}'".format(args.app) if args.app else "default "
        self.logger.info("The {} app could be opened".format(info_msg))
