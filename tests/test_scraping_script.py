"""Module that defines tests for :mod:`~lyrics_scraping.scripts.scraping`

The script ``scraping.py`` is tested here with different combinations of
command-line options.

"""

import sys
import time
import unittest

from .utils import TestLyricsScraping
from lyrics_scraping.scripts import scraping
from lyrics_scraping.utils import get_data_filepath
from pyutils.genutils import get_module_filename, get_qualname, load_yaml


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
        self._test_config_method(args=['-e', 'log'])

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
        self._test_config_method(args=['-e', 'main'])

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
        self._test_config_method(args=['--edit', 'log', '--app_name', 'TextEdit'])

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
        self._test_config_method(args=['-e', 'main', '-a', 'TextEdit'])

    # @unittest.skip("test_edit_config_case_5()")
    def test_edit_config_case_5(self):
        """Test edit_config() when a non-existing app is given.

        Case 5 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        returns 1 when a non-existing app is given for editing the logging
        config file.

        """
        self.log_test_method_name()
        self._test_config_method(args=['-e', 'main', '-a', 'WrongApp'],
                                 expected_retcode=1, seconds=0)

    # @unittest.skip("test_reset_config_case_1()")
    def test_reset_config_case_1(self):
        """Test that reset_config() resets the log config file.

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        resets the user-defined log config file with factory default values.

        """
        self.log_test_method_name()
        self._test_config_method(args=['-r', 'main'], seconds=0)

    @unittest.skip("test_reset_config_case_2()")
    def test_reset_config_case_2(self):
        """Test that reset_config() resets the main config file.

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        resets the user-defined main config file with factory default values.

        """
        self.log_test_method_name()
        self.logger.info("Testing <color>reset_config()</color>...")

    @unittest.skip("test_reset_config_case_3()")
    def test_reset_config_case_3(self):
        """Test reset_config() when a non-existing config file is given.

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        returns 1 when a non-existing config file is given.

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

    def _test_config_method(self, args, expected_retcode=0, seconds=1):
        """TODO: Test that main() and edit_config() calls an external app to edit a
        config file.

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

        TODO: main and setup_arg_parser are also being tested

        Parameters
        ----------
        args
        expected_retcode
        seconds

        """
        # TODO: explain
        case = self._testMethodName.split("case_")[-1]
        valid_config_methods = ["edit_config", "reset_config"]
        config_method = self._testMethodName.split("test_")[1].split("_case")[0]
        assert config_method in valid_config_methods, \
            "Wrong config method detected: '{}' (valid methods are {})".format(
                config_method, ", ".join(config_method))
        sys.argv = [get_module_filename(scraping)]
        sys.argv.extend(args)
        p_args = scraping.setup_arg_parser()
        app_type = "'{}'".format(p_args.app) if p_args.app else "default"
        # Build main message for info logging
        info_msg = "Case <color>{}</color> of testing <color>{}()</color> " \
                   "with the <color>{}</color> config file".format(
                      case,
                      config_method,
                      p_args.edit if p_args.edit else p_args.reset)
        if config_method == "edit_config":
            info_msg += " and the <color>{}</color> app".format(app_type)
        info_msg += "\n<color>Args:</color> {}".format(args)
        self.logger.info(info_msg)
        if config_method == "edit_config":
            self._test_edit_config(app_type, expected_retcode, seconds)
        else:
            self._test_reset_config(p_args.reset, app_type, expected_retcode,
                                    seconds)

    def _test_edit_config(self, app_type, expected_retcode, seconds):
        """TODO

        Parameters
        ----------
        app_type
        expected_retcode
        seconds

        """
        # TODO: explain
        # Call the main function with arguments
        # NOTE: setup_arg_parser() is called again in main()
        retcode = scraping.main()
        if expected_retcode == 0:
            assert_msg = "The {} app couldn't be open. Return code is " \
                         "{}".format(app_type, retcode)
            info_msg = "The {} app was called <color>as expected</color>"
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info(info_msg.format(app_type))
            time.sleep(seconds)
        else:
            assert_msg = "Very highly unlikely case. The rules of reality " \
                         "were bent to get you here! Return code " \
                         "is".format(retcode)
            info_msg = "The {} app couldn't be called <color>as expected</color>"
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info(info_msg.format(app_type))

    def _test_reset_config(self, cfg_type, app_type, expected_retcode, seconds):
        """TODO

        Parameters
        ----------
        cfg_type
        app_type
        expected_retcode
        seconds

        """
        # TODO: explain
        # Call the main function with arguments
        # NOTE: setup_arg_parser() is called again in main()
        retcode = scraping.main()
        if expected_retcode == 0:
            assert_msg = "The {} config file couldn't be reset. Return code is " \
                         "{}".format(cfg_type, retcode)
            self.assertTrue(retcode == expected_retcode, assert_msg)
            # Test that the config file was really reset by checking its content
            default_cfg_filepath = get_data_filepath(
                file_type='default_{}'.format(cfg_type))
            user_cfg_filepath = get_data_filepath(file_type=cfg_type)
            default_cfg_dict = load_yaml(default_cfg_filepath)
            user_cfg_dict = load_yaml(user_cfg_filepath)
            assert_msg = "The {} config file was not reset as " \
                         "expected".format(cfg_type)
            self.assertDictEqual(default_cfg_dict, user_cfg_dict, assert_msg)
            self.logger.info("The {} config file was reset <color>as "
                             "expected</color>".format(cfg_type))
            time.sleep(seconds)
        else:
            assert_msg = "Very highly unlikely case. The rules of reality " \
                         "were bent to get you here! Return code " \
                         "is".format(retcode)
            info_msg = "The {} config file couldn't be reset <color>as " \
                       "expected</color>".format(cfg_type)
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info(info_msg.format(app_type))
