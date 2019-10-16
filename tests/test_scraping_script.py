"""Module that defines tests for :mod:`~lyrics_scraping.scripts.scraping`

The script ``scraping.py`` is tested here with different combinations of
command-line options.

"""

import argparse
import sys
import time
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
        """Test edit_config() when a default app is used for editing the
        logging config file.

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the default app for editing the logging config file.

        For example, the default app as determined by the OS can be TextEdit or
        atom.

        """
        self.log_test_method_name()
        self._test_edit_config(args=['-e', 'log'])

    # Skip test if on PROD because we are opening an app to edit a file
    @unittest.skipIf(TestLyricsScraping.env_type == "PROD", "Skip if on PROD")
    def test_edit_config_case_2(self):
        """Test edit_config() when a default app is used for editing the main
        config file.

        Case 2 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the default app for editing the main config file.

        For example, the default app as determined by the OS can be TextEdit or
        atom.

        """
        self.log_test_method_name()
        self._test_edit_config(args=['-e', 'main'])

    # Skip test if on PROD because we are opening an app to edit a file
    @unittest.skipIf(TestLyricsScraping.env_type == "PROD", "Skip if on PROD")
    def test_edit_config_case_3(self):
        """Test edit_config() when a user-selected app is given for editing the
        logging config file.

        Case 3 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the use-selected app for editing the logging config file.

        For example, the app can be TextEdit or atom.

        Also, this test makes use of the long form of the edit and app
        arguments.

        """
        self.log_test_method_name()
        self._test_edit_config(args=['--edit', 'log', '--app_name', 'TextEdit'])

    # Skip test if on PROD because we are opening an app to edit a file
    @unittest.skipIf(TestLyricsScraping.env_type == "PROD", "Skip if on PROD")
    def test_edit_config_case_4(self):
        """Test edit_config() when a user-selected app is given for editing
        the main config file.

        Case 4 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the user-selected app for editing the main config file.

        For example, the app can be TextEdit or atom.

        """
        self.log_test_method_name()
        self._test_edit_config(args=['-e', 'main', '-a', 'TextEdit'])

    # @unittest.skip("test_edit_config_case_5()")
    def test_edit_config_case_5(self):
        """Test edit_config() when a non-existing app is given.

        Case 5 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        returns 1 when a non-existing app is given for editing the logging
        config file.

        """
        self.log_test_method_name()
        self._test_edit_config(args=['-e', 'main', '-a', 'WrongApp'],
                               expected_retcode=1)

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

    def _test_edit_config(self, args, expected_retcode=0, seconds=1):
        """Test that main() and edit_config() can call an external app to edit
        a config file.

        Depending on `args` given to :meth:`~lyrics_scraping.scripts.main`, a
        default or user-selected app will be called to edit a config file which
        can either be the main or logging config file.

        :meth:`~lyrics_scraping.scripts.main` reads `args` but then it delegates
        the task of calling the external editing app to
        :meth:`~lyrics_scraping.scripts.edit_config`.

        `expected_retcode` is used in case you want to test a case where `args`
        will cause :meth:`~lyrics_scraping.scripts.edit_config` to not
        be able to call the external app.

        You can insert a certain delay of `seconds` between each call to this
        function. Hence, you can avoid having many consecutively windows being
        opened very quickly.

        Parameters
        ----------
        args : list of str
        expected_retcode : int
        seconds : int or float
            TODO: check the time.sleep doc

        """
        # TODO: explain
        case = self._testMethodName.split("case_")[-1]
        parser = argparse.ArgumentParser()
        parser.add_argument("-e", "--edit", choices=["log", "main"])
        parser.add_argument("-a", "--app_name", default=None, dest="app")
        p_args = parser.parse_args(args)
        app_type = "'{}'".format(p_args.app) if p_args.app else "default"
        info_msg = "Case {} of testing <color>edit_config()" \
                   "</color> with the <color>{}</color> config file and the " \
                   "<color>{}</color> app".format(case, p_args.edit, app_type)
        info_msg += "\n<color>Args:</color> {}".format(args)
        self.logger.info(info_msg)
        sys.argv = [get_module_filename(scraping)]
        sys.argv.extend(args)
        # Call the main function with arguments
        retcode = scraping.main()
        if expected_retcode == 0:
            msg = "The {} app couldn't be open. Return code is " \
                  "{}".format(app_type, retcode)
            self.assertTrue(retcode == expected_retcode, msg)
            self.logger.info("The {} app could be called".format(app_type))
            time.sleep(seconds)
        else:
            msg = "Very highly unlikely case. The rules of reality were bent " \
                  "to get you here! Return code is".format(retcode)
            self.assertTrue(retcode == expected_retcode, msg)
            self.logger.info("The {} app couldn't be called".format(app_type))
