"""Module that defines tests for :mod:`~lyrics_scraping.scripts.scraping`

The script ``scraping.py`` is tested here with different combinations of
command-line options.

"""

from collections import namedtuple
import sys
import time
import unittest

from .utils import TestLyricsScraping, modify_and_restore, move_and_restore
from lyrics_scraping.scripts import scraping
from lyrics_scraping.utils import load_cfg
from pyutils.genutils import get_module_filename, get_qualname
from pyutils.logutils import setup_basic_logger


class TestScrapingScript(TestLyricsScraping):
    # TODO
    TEST_MODULE_QUALNAME = get_qualname(scraping)
    LOGGER_NAME = __name__
    SHOW_FIRST_CHARS_IN_LOG = 0

    @classmethod
    def setUpClass(cls):
        """TODO
        """
        super().setUpClass()
        # Setup logging for scraping module
        import ipdb
        ipdb.set_trace()
        scraping.logger = setup_basic_logger(name=scraping.logger.name,
                                             add_console_handler=True,
                                             remove_all_handlers=True)

    # @unittest.skip("test_edit_config_case_1()")
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
        self._test_edit_config(args=['-e', 'log'])

    @unittest.skip("test_edit_config_case_2()")
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
        self._test_edit_config(args=['-e', 'main'])

    @unittest.skip("test_edit_config_case_3()")
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
        self._test_edit_config(args=['--edit', 'log', '-a', 'TextEdit'])

    @unittest.skip("test_edit_config_case_4()")
    # Skip test if on PROD because we are opening an app to edit a file
    @unittest.skipIf(TestLyricsScraping.env_type == "PROD", "Skip if on PROD")
    def test_edit_config_case_4(self):
        """Test edit_config() when a user-selected app is given for editing
        the main config file.

        Case 4 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        opens the user-selected app for editing the main config file.

        For example, the app can be TextEdit or atom.

        """
        self._test_edit_config(args=['-e', 'main', '--app_name', 'TextEdit'])

    @unittest.skip("test_edit_config_case_5()")
    def test_edit_config_case_5(self):
        """Test edit_config() when a non-existing app is given.

        Case 5 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        returns 1 when a non-existing app is given for editing the logging
        config file.

        """
        self._test_edit_config(args=['-e', 'main', '-a', 'WrongApp'],
                               expected_retcode=1, seconds=0)

    @unittest.skip("test_edit_config_case_6()")
    @move_and_restore("log")
    def test_edit_config_case_6(self):
        """Test edit_config() when the log config file is not found.

        TODO: check description

        Case 6 tests that :meth:`~lyrics_scraping.scripts.scraper.edit_config`
        returns 1 when the log config file is not found.

        """
        self._test_edit_config(args=['-e', 'log', '-a', 'TextEdit'],
                               expected_retcode=1, seconds=0)

    @unittest.skip("test_reset_config_case_1()")
    @modify_and_restore(cfg_type="log")
    def test_reset_config_case_1(self):
        """Test that reset_config() resets the log config file.

        TODO: check description

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        resets the user-defined log config file with factory default values.

        """
        self._test_reset_config(args=['-r', 'log'])

    @unittest.skip("test_reset_config_case_2()")
    @modify_and_restore(cfg_type="main")
    def test_reset_config_case_2(self):
        """Test that reset_config() resets the main config file.

        TODO: check description

        Case 2 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        resets the user-defined main config file with factory default values.

        """
        self._test_reset_config(args=['-r', 'main'])

    @unittest.skip("test_reset_config_case_3()")
    @move_and_restore("main")
    def test_reset_config_case_3(self):
        """Test reset_config() when the main config file is not found.

        TODO: check description

        Case 3 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        returns 1 when the main config file is not found.

        """
        # TODO: explain
        cfg_type = "main"
        extra_msg = "Case where the <color>{}</color> config file is " \
                    "<color>not found</color>".format(cfg_type)
        # Reset the config file which is not to be found
        self._test_reset_config(args=['-r', cfg_type],
                                expected_retcode=1,
                                extra_main_msg=extra_msg)

    @unittest.skip("test_reset_config_case_4()")
    @modify_and_restore(cfg_type="main")
    def test_reset_config_case_4(self):
        """Test reset_config() when the main config file is reset twice in a
        row.

        TODO: check description

        Case 4 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        returns 2 when the main config file is reset twice in a row.

        """
        # TODO: explain
        cfg_type = "main"
        # First RESET
        extra_msg = "Case where the <color>{}</color> config file is <color>" \
                    "reset twice</color> in a row\n".format(cfg_type)
        extra_msg += "<color>RESET #1</color>"
        self._test_reset_config(args=['-r', cfg_type],
                                expected_retcode=0,
                                extra_main_msg=extra_msg,
                                undo_reset=False)
        # Second RESET
        extra_msg = "<color>RESET #2</color>"
        self._start_newline = False
        self._test_reset_config(args=['-r', cfg_type],
                                expected_retcode=2,
                                extra_main_msg=extra_msg)
        self._start_newline = True

    @unittest.skip("test_undo_config_case_1()")
    @modify_and_restore(cfg_type="log", reset_first=True,
                        check_modified_cfg=True)
    def test_undo_config_case_1(self):
        """Test that undo_config() restores the log config file.

        TODO: check description

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.undo_config`
        restores the user-defined log config file to what it was before the
        last reset.

        """
        # Undo the config file
        self._test_undo_config(args=['-u', 'log'])

    @unittest.skip("test_undo_config_case_2()")
    @modify_and_restore(cfg_type="main", reset_first=True,
                        check_modified_cfg=True)
    def test_undo_config_case_2(self):
        """Test that undo_config() restores the main config file.

        TODO: check description

        Case 2 tests that :meth:`~lyrics_scraping.scripts.scraper.undo_config`
        restores the user-defined main config file to what it was before the
        last reset.

        """
        # Undo the config file
        self._test_undo_config(args=['-u', 'main'])

    @unittest.skip("test_undo_config_case_3()")
    @move_and_restore("main")
    def test_undo_config_case_3(self):
        """Test undo_config() when the main config file is not found.

        TODO: check description, difficult to simulate this case

        Case 3 tests that :meth:`~lyrics_scraping.scripts.scraper.undo_config`
        returns 1 when the main config file is not found.

        """
        # TODO: explain
        cfg_type = "main"
        extra_msg = "Case where the <color>{}</color> config file is " \
                    "<color>not found</color>".format(cfg_type)
        # Undo the config file which is not to be found
        self._test_undo_config(args=['-u', cfg_type],
                               expected_retcode=1,
                               extra_main_msg=extra_msg)

    @unittest.skip("test_undo_config_case_4()")
    @modify_and_restore(cfg_type="main", reset_first=True)
    def test_undo_config_case_4(self):
        """Test undo_config() when the main config file is undo twice in a
        row.

        TODO: check description

        Case 4 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        returns 2 when the main config file is undo (restored) twice in a row.

        """
        # TODO: explain
        cfg_type = "main"
        # First UNDO
        extra_msg = "Case where the <color>{}</color> config file is <color>" \
                    "undo twice</color> in a row\n".format(cfg_type)
        extra_msg += "<color>UNDO #1</color>"
        self._test_undo_config(args=['-u', cfg_type],
                               expected_retcode=0,
                               extra_main_msg=extra_msg)
        # Second UNDO
        extra_msg = "<color>UNDO #2</color>"
        self._start_newline = False
        self._test_undo_config(args=['-u', cfg_type],
                               expected_retcode=2,
                               extra_main_msg=extra_msg)
        self._start_newline = True

    @unittest.skip("test_setup_argparser_case_1()")
    def test_setup_argparser_case_1(self):
        """TODO
        """
        self._test_setup_argparser(['-e', 'log'], "edit")

    @unittest.skip("test_setup_argparser_case_2()")
    def test_setup_argparser_case_2(self):
        """TODO
        """
        self._test_setup_argparser(['-r', 'main'], "reset")

    @unittest.skip("test_setup_argparser_case_3()")
    def test_setup_argparser_case_3(self):
        """TODO
        """
        self._test_setup_argparser(['-s'], "start_scraper")

    @unittest.skip("test_setup_argparser_case_4()")
    def test_setup_argparser_case_4(self):
        """TODO
        """
        self._test_setup_argparser(['-u', 'log'], "undo")

    @unittest.skip("test_setup_argparser_case_5()")
    def test_setup_argparser_case_5(self):
        """TODO
        """
        self._test_setup_argparser(['-x'], "invalid_argument")

    @unittest.skip("test_start_scraper()")
    def test_start_scraper(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>start_scraper()</color>...")

    def _test_setup_argparser(self, args, expected_action, extra_msg=None):
        self.log_test_method_name()
        case, cfg_func = self.process_test_method_name()
        info_msg = "Case <color>{}</color> of testing <color>{}()" \
                   "</color>".format(case, cfg_func)
        info_msg += "\n<color>Args:</color> {}".format(args)
        self.logger.info(info_msg)
        if extra_msg:
            self.logger.info("\n{}".format(extra_msg))
        sys.argv = [get_module_filename(scraping)]
        sys.argv.extend(args)
        try:
            # Parse args
            p_args = scraping.setup_argparser()
            assert_msg = "The parsed arguments doesn't contain the expected " \
                         "action '{}'".format(expected_action)
            self.assertTrue(p_args.__contains__(expected_action), assert_msg)
            self.logger.info("Parsed arguments <color>as expected</color>")
        except SystemExit:
            if expected_action == "invalid_argument":
                self.logger.info("Invalid argument {} <color>as expected"
                                 "</color>".format(args[0]))
            else:
                self.fail("Extremely odd case!")

    def parse_args(self, args, extra_main_msg):
        """TODO

        Parameters
        ----------
        args
        extra_main_msg

        Returns
        -------

        """
        # TODO: explain
        self.log_test_method_name()
        case = self._testMethodName.split("case_")[-1]
        valid_cfg_funcs = ["edit_config", "reset_config", "undo_config"]
        cfg_func = self._testMethodName.split("test_")[1].split("_case")[0]
        assert cfg_func in valid_cfg_funcs, \
            "Wrong config function detected: '{}' (valid functions are " \
            "{})".format(cfg_func, ", ".join(valid_cfg_funcs))
        sys.argv = [get_module_filename(scraping)]
        sys.argv.extend(args)
        # Parse args
        p_args = scraping.setup_argparser()
        # Build main message for info logging
        if p_args.edit:
            cfg_type = p_args.edit
        elif p_args.reset:
            cfg_type = p_args.reset
        else:
            assert p_args is not None, "No config file found"
            cfg_type = p_args.undo
        info_msg = "Case <color>{}</color> of testing <color>{}()</color> " \
                   "with the <color>{}</color> config file".format(
                    case,
                    cfg_func,
                    cfg_type)
        if cfg_func == "edit_config":
            app_type = "'{}'".format(p_args.app) if p_args.app else "default"
            info_msg += " and the <color>{}</color> app".format(app_type)
        else:
            # No app associated with the other config functions
            app_type = None
        info_msg += "\n<color>Args:</color> {}".format(args)
        if extra_main_msg:
            info_msg += "\n{}".format(extra_main_msg)
        self.logger.info(info_msg)
        results = namedtuple("results", "app_type cfg_type")
        results.app_type = app_type
        results.cfg_type = cfg_type
        return results

    def _test_edit_config(self, args, expected_retcode=0, seconds=2,
                          extra_main_msg=None):
        """TODO

        Parameters
        ----------
        args
        expected_retcode
        seconds
        extra_main_msg

        """
        # TODO: explain
        results = self.parse_args(args, extra_main_msg)
        app_type = results.app_type
        # Call main() with the given arguments
        # NOTE: setup_arg_parser() is called in main()
        retcode = scraping.main()
        if expected_retcode == 0:
            assert_msg = "The {} app couldn't be open. Return code is " \
                         "{}".format(app_type, retcode)
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info("The {} app was called <color>as expected"
                             "</color>".format(app_type))
            time.sleep(seconds)
        else:
            assert_msg = "Very highly unlikely case. Return code " \
                         "is".format(retcode)
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info("The {} app couldn't be called <color>as "
                             "expected</color>".format(app_type))

    def _test_reset_config(self, args, expected_retcode=0, extra_main_msg=None,
                           undo_reset=True):
        """TODO

        Parameters
        ----------
        args
        expected_retcode
        extra_main_msg
        undo_reset

        """
        # TODO: explain
        results = self.parse_args(args, extra_main_msg)
        cfg_type = results.cfg_type
        # Call main() with the given arguments
        # NOTE: setup_arg_parser() is called within main()
        retcode = scraping.main()
        if expected_retcode == 0:  # Success: config file reset
            assert_msg = "The {} config file couldn't be reset. Return code " \
                         "is {}".format(cfg_type, retcode)
            self.assertTrue(retcode == expected_retcode, assert_msg)
            # Test that the config file was really reset by checking its content
            default_cfg_dict = load_cfg('default_' + cfg_type)
            user_cfg_dict = load_cfg(cfg_type)
            assert_msg = "The {} config file was not reset as " \
                         "expected".format(cfg_type)
            self.assertDictEqual(default_cfg_dict, user_cfg_dict, assert_msg)
            self.logger.info("The {} config file was reset <color>as "
                             "expected</color>".format(cfg_type))
            if undo_reset:
                # Undo the reset
                retcode = scraping.undo_config(cfg_type)
                assert_msg = "The last RESET couldn't be undo"
                self.assertTrue(retcode == 0, assert_msg)
                self.logger.info("The {} config file was successfully reverted "
                                 "<color>as expected</color>".format(cfg_type))
        elif expected_retcode == 1:  # ERROR
            self.assert_retcode_when_fail(cfg_type, retcode, expected_retcode,
                                           "reset")
        elif expected_retcode == 2:  # Config file ALREADY reset
            self.assert_retcode_when_fail(cfg_type, retcode, expected_retcode,
                                           "reset")
        else:
            self.fail("Very odd! Return code ({}) not as expected "
                      "({})".format(retcode, expected_retcode))

    def _test_undo_config(self, args, expected_retcode=0, extra_main_msg=None):
        """TODO

        Parameters
        ----------
        args
        expected_retcode
        extra_main_msg

        """
        results = self.parse_args(args, extra_main_msg)
        cfg_type = results.cfg_type
        # Call main() with the given arguments
        # NOTE: setup_arg_parser() is called within main()
        retcode = scraping.main()
        if expected_retcode == 0:  # Success: config file restored
            assert_msg = "The {} config file couldn't be restored. Return " \
                         "code is {}".format(cfg_type, retcode)
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info("The {} config file was successfully restored "
                             "<color>as expected</color>".format(cfg_type))
        elif expected_retcode == 1:  # ERROR
            self.assert_retcode_when_fail(cfg_type, retcode, expected_retcode,
                                           "restored")
        elif expected_retcode == 2:  # Config file already restored
            self.assert_retcode_when_fail(cfg_type, retcode, expected_retcode,
                                           "restored")
        else:
            self.fail("Very odd! Return code ({}) not as expected "
                      "({})".format(retcode, expected_retcode))

    def assert_retcode_when_fail(self, cfg_type, retcode, expected_retcode, action):
        """TODO

        Parameters
        ----------
        cfg_type
        retcode
        expected_retcode
        action

        """
        valid_expected_retcodes = [1, 2]
        valid_as_str = ", ".join(map(str, valid_expected_retcodes))
        assert expected_retcode in valid_expected_retcodes, \
            "Wrong expected rectcode: '{}' (valid expected rectcodes are " \
            "{})".format(expected_retcode, valid_as_str)
        assert_msg = "Return code ({}) not as expected " \
                     "({})".format(retcode, expected_retcode)
        self.assertTrue(retcode == expected_retcode, assert_msg)
        self.logger.info("The {} config file couldn't be {} <color>"
                         "as expected</color>".format(cfg_type, action))
