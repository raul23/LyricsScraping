"""TODO
"""

import functools
import os
import shutil

from pyutils.testutils import TestBase
from lyrics_scraping.utils import (
    dump_cfg, get_bak_cfg_filepath, get_data_filepath, load_cfg)


class TestLyricsScraping(TestBase):
    # TODO
    TEST_MODULE_QUALNAME = "module"
    CREATE_TEST_DATABASE = False
    ADD_FILE_HANDLER = True
    LOGGER_NAME = __name__
    LOGGING_FILENAME = "scraping.log"
    SHOW_FIRST_CHARS_IN_LOG = 1000
    SCHEMA_FILEPATH = None
    DB_FILENAME = "db.qlite"


# Decorator
def backup_modify_restore(cfg_type):
    """TODO

    Parameters
    ----------
    cfg_type

    Returns
    -------

    """

    def decorator_backup_modify_restore(func):
        """TODO

        Parameters
        ----------
        func

        Returns
        -------

        """

        @functools.wraps(func)
        def wrapper_backup_modify_restore(self, *args, **kwargs):
            """TODO

            Parameters
            ----------
            self
            args
            kwargs

            """
            # TODO: explain, need to modify cfg file, copy the backup
            # config file
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
            # Reset or undo config file
            func(self, *args, **kwargs)
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

        return wrapper_backup_modify_restore

    return decorator_backup_modify_restore


# Decorator
def move_and_restore(cfg_type):
    """TODO

    Parameters
    ----------
    cfg_type

    Returns
    -------

    """

    def decorator_move_and_restore(func):
        """TODO

        Parameters
        ----------
        func

        Returns
        -------

        """

        @functools.wraps(func)
        def wrapper_move_and_restore(self, *args, **kwargs):
            """TODO

            Parameters
            ----------
            self
            args
            kwargs

            """
            # TODO: explain
            # Move the config file so that it seems that it is not found anymore
            cfg_filepath = get_data_filepath(cfg_type)
            orig_cfg_dict = load_cfg(cfg_type)
            tmp_cfg_filepath = cfg_filepath + ".tmp"
            shutil.move(cfg_filepath, tmp_cfg_filepath)
            # Edit or reset
            func(self, *args, **kwargs)
            # Move the config file back to its original location
            shutil.move(tmp_cfg_filepath, cfg_filepath)
            cfg_dict = load_cfg(cfg_type)
            assert_msg = "The {} config file is not the same as the original " \
                         "one".format(cfg_type)
            self.assertDictEqual(orig_cfg_dict, cfg_dict, assert_msg)
            self.logger.info("The {} config file was successfully moved to its "
                             "original location".format(cfg_type))

        return wrapper_move_and_restore

    return decorator_move_and_restore
