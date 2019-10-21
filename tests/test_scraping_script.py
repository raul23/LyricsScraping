"""Module that defines tests for :mod:`~lyrics_scraping.scripts.scraping`

The script ``scraping.py`` is tested here with different combinations of
command-line options.

"""

from collections import namedtuple
import sys
import time
import unittest

from .utils import TestLyricsScraping, backup_modify_restore, move_and_restore
from lyrics_scraping.scripts import scraping
from lyrics_scraping.utils import load_cfg
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
        self._test_edit_config(args=['--edit', 'log', '-a', 'TextEdit'])

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
    @backup_modify_restore(cfg_type="log")
    def test_reset_config_case_1(self):
        """Test that reset_config() resets the log config file.

        TODO: check description

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        resets the user-defined log config file with factory default values.

        """
        self._test_reset_config(args=['-r', 'log'])

    @unittest.skip("test_reset_config_case_2()")
    @backup_modify_restore(cfg_type="main")
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
    @backup_modify_restore(cfg_type="main")
    def test_reset_config_case_4(self):
        """Test reset_config() when the main config file is reset twice in a
        row.

        TODO: check description

        Case 4 tests that :meth:`~lyrics_scraping.scripts.scraper.reset_config`
        returns 2 when the main config file is reset twice in a row.

        """
        self._test_two_reset_config('main')

    # @unittest.skip("test_undo_config_case_1()")
    # @backup_modify_restore(cfg_type="log")
    def test_undo_config_case_1(self):
        """Test that undo_config() restores the log config file.

        TODO: check description

        Case 1 tests that :meth:`~lyrics_scraping.scripts.scraper.undo_config`
        restores the user-defined log config file to what it was before the
        last reset.

        """
        import os
        import shutil
        from lyrics_scraping.utils import dump_cfg, get_bak_cfg_filepath, get_data_filepath
        cfg_type = "log"
        import ipdb
        ipdb.set_trace()
        # Copy the backup config file if it is there
        found_backup_cfg = False
        if os.path.isfile(get_bak_cfg_filepath(cfg_type)):
            found_backup_cfg = True
            shutil.copy(get_bak_cfg_filepath(cfg_type),
                        get_bak_cfg_filepath(cfg_type) + ".tmp")
        # Modify the log config file
        shutil.copy(get_data_filepath(cfg_type),
                    get_data_filepath(cfg_type) + ".tmp")
        cfg_dict = load_cfg(cfg_type)
        cfg_dict['new_option'] = 22
        dump_cfg(get_data_filepath(cfg_type), cfg_dict)
        # Undo the config file
        self._test_undo_config(args=['-u', 'log'])
        # Undo the changes to the config file
        shutil.move(get_data_filepath(cfg_type) + ".tmp",
                    get_data_filepath(cfg_type))
        self.logger.info("{} config file restored".format(cfg_type))
        # Restore the backup config file
        if found_backup_cfg:
            shutil.move(get_bak_cfg_filepath(cfg_type) + ".tmp",
                        get_bak_cfg_filepath(cfg_type))
            self.logger.info("Backup {} config file "
                             "restored".format(cfg_type))
        elif os.path.isfile(get_bak_cfg_filepath(cfg_type)):
            # Remove backup config file since it wasn't there in the
            # beginning
            os.unlink(get_bak_cfg_filepath(cfg_type))
            self.logger.info("Backup {} config file "
                             "removed".format(cfg_type))

    @unittest.skip("test_setup_arg_parser_case_1()")
    def test_setup_arg_parser_case_1(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>setup_arg_parser()</color>...")

    @unittest.skip("test_setup_arg_parser_case_2()")
    def test_setup_arg_parser_case_2(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>setup_arg_parser()</color>...")

    @unittest.skip("test_start_scraper()")
    def test_start_scraper(self):
        """TODO
        """
        self.log_test_method_name()
        self.logger.info("Testing <color>start_scraper()</color>...")

    def _log_main_info_msg_for_cfg_method(self, args, extra_main_msg):
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
        valid_config_funcs = ["edit_config", "reset_config", "undo_config"]
        config_func = self._testMethodName.split("test_")[1].split("_case")[0]
        assert config_func in valid_config_funcs, \
            "Wrong config function detected: '{}' (valid functions are " \
            "{})".format(config_func, ", ".join(valid_config_funcs))
        sys.argv = [get_module_filename(scraping)]
        sys.argv.extend(args)
        p_args = scraping.setup_arg_parser()
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
                    config_func,
                    cfg_type)
        if config_func == "edit_config":
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
        results = self._log_main_info_msg_for_cfg_method(args, extra_main_msg)
        app_type = results.app_type
        # Call main() with the given arguments
        # NOTE: setup_arg_parser() is called in main()
        retcode = scraping.main()
        if expected_retcode == 0:
            assert_msg = "The {} app couldn't be open. Return code is " \
                         "{}".format(app_type, retcode)
            info_msg = "The {} app was called <color>as expected</color>"
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info(info_msg.format(app_type))
            time.sleep(seconds)
        else:
            assert_msg = "Very highly unlikely case. Return code " \
                         "is".format(retcode)
            info_msg = "The {} app couldn't be called <color>as expected" \
                       "</color>".format(app_type)
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info(info_msg)

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
        results = self._log_main_info_msg_for_cfg_method(args, extra_main_msg)
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
        elif expected_retcode in [1, 2]:  # ERROR or Config file ALREADY reset
            assert_msg = "Return code ({}) not as expected " \
                         "({})".format(retcode, expected_retcode)
            info_msg = "The {} config file couldn't be reset <color>as " \
                       "expected</color>".format(cfg_type)
            self.assertTrue(retcode == expected_retcode, assert_msg)
            self.logger.info(info_msg)
        else:
            self.fail("Very odd! Return code ({}) not as expected "
                      "({})".format(retcode, expected_retcode))

    def _test_two_reset_config(self, cfg_type):
        """TODO

        Parameters
        ----------
        cfg_type

        """
        # TODO: explain
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

    def _test_undo_config(self, args, expected_retcode=0, extra_main_msg=None):
        """TODO

        Parameters
        ----------
        args
        expected_retcode
        extra_main_msg
        undo_reset

        """
        results = self._log_main_info_msg_for_cfg_method(args, extra_main_msg)
        cfg_type = results.cfg_type
        # Call main() with the given arguments
        # NOTE: setup_arg_parser() is called within main()
        retcode = scraping.main()
