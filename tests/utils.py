"""TODO
"""

import functools
import os
import shutil

from lyrics_scraping.utils import (
    dump_cfg, get_backup_cfg_filepath, get_data_filepath, load_cfg)
from pyutils.testutils import TestBase


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
def modify_and_restore(cfg_type):
    """TODO

    Parameters
    ----------
    cfg_type
    reset_first
    check_modified_cfg

    Returns
    -------

    """

    def decorator_modify_and_restore(func):
        """TODO

        Parameters
        ----------
        func

        Returns
        -------

        """

        @functools.wraps(func)
        def wrapper_modify_and_restore(self, *args, **kwargs):
            """TODO

            Parameters
            ----------
            self
            args
            kwargs

            """
            # TODO: explain, need to modify cfg file, copy the backup
            # config file
            # ============
            # Modification
            # ============
            cfg_file = _ConfigFile(cfg_type)
            backup_cfg_file = _BackupConfigFile(cfg_type)
            # Move the backup config file if there is one
            backup_cfg_file.move()
            # Modify the config file
            cfg_file.modify()
            # ==================
            # Decorated function
            # ==================
            # Perform action on config file
            func(self, *args, **kwargs)
            # ===========
            # Restoration
            # ===========
            # Check that the file is reverted back to its original modification
            # TODO: explain that it is our duty to revert the file to what it
            # was before the call to the decorated function
            cfg_file.check_cfg()
            # Undo the original change to the config file
            cfg_file.restore()
            # Restore the backup config file if there was one in the beginning
            backup_cfg_file.restore()

        return wrapper_modify_and_restore

    return decorator_modify_and_restore


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
            # ================
            # Move config file
            # ================
            cfg_file = _ConfigFile(cfg_type)
            backup_cfg_file = _BackupConfigFile(cfg_type)
            # Move the config file so that it seems that it is not found anymore
            cfg_file.move()
            # Move the backup config file if it is there
            backup_cfg_file.move()
            # ==================
            # Decorated function
            # ==================
            func(self, *args, **kwargs)
            # ===========
            # Restoration
            # ===========
            # Move the config file back to its original location
            cfg_file.restore()
            # Restore the backup config file
            backup_cfg_file.restore()

        return wrapper_move_and_restore

    return decorator_move_and_restore


class _ConfigFile:
    """TODO
    """
    def __init__(self, cfg_type):
        self._cfg_type = cfg_type
        self._orig_cfg_dict =  load_cfg(self._cfg_type)
        self._cfg_filepath = get_data_filepath(self._cfg_type)
        self._tmp_cfg_filepath = self._cfg_filepath + ".tmp"
        self._new_opt_key = "new_option"
        self._new_opt_val = 22
        self._new_option = {self._new_opt_key: self._new_opt_val}

    def check_cfg(self):
        cfg_dict = load_cfg(self._cfg_type)
        assert_msg = "The {} config file was not reverted " \
                     "correctly".format(self._cfg_type)
        assert cfg_dict.get(self._new_opt_key) == self._new_opt_val, \
            assert_msg

    def modify(self):
        shutil.copy(get_data_filepath(self._cfg_type),
                    get_data_filepath(self._cfg_type) + ".tmp")
        cfg_dict = load_cfg(self._cfg_type)
        cfg_dict.update(self._new_option)
        dump_cfg(get_data_filepath(self._cfg_type), cfg_dict)

    def move(self):
        """TODO
        """
        shutil.move(self._cfg_filepath, self._tmp_cfg_filepath)

    def restore(self):
        """TODO
        """
        shutil.move(self._tmp_cfg_filepath, self._cfg_filepath)
        cfg_dict = load_cfg(self._cfg_type)
        assert_msg = "The {} config file is not the same as the original " \
                     "one".format(self._cfg_type)
        assert self._orig_cfg_dict == cfg_dict, assert_msg


class _BackupConfigFile:
    """TODO
    """
    def __init__(self, cfg_type):
        self._cfg_type = cfg_type
        self._found_backup_cfg = False

    def move(self):
        """TODO
        """
        if os.path.isfile(get_backup_cfg_filepath(self._cfg_type)):
            self._found_backup_cfg = True
            # TODO: move (instead of copy) backup file?
            shutil.move(get_backup_cfg_filepath(self._cfg_type),
                        get_backup_cfg_filepath(self._cfg_type) + ".tmp")

    def restore(self):
        """TODO
        """
        if self._found_backup_cfg:
            shutil.move(get_backup_cfg_filepath(self._cfg_type) + ".tmp",
                        get_backup_cfg_filepath(self._cfg_type))
        elif os.path.isfile(get_backup_cfg_filepath(self._cfg_type)):
            # Remove backup config file since it wasn't there in the
            # beginning
            os.unlink(get_backup_cfg_filepath(self._cfg_type))
