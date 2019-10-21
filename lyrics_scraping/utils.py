"""Collection of utilities specifically for the lyrics scraping project.

.. _default logging configuration file: https://bit.ly/2oPJSr4
.. _default main configuration file: https://bit.ly/2n764MV
.. _user-defined logging configuration file: https://bit.ly/2niTDgY
.. _user-defined main configuration file: https://bit.ly/2oyt0VJ
.. _SQL schema file music.sql: https://bit.ly/2kIMYvn

"""

from collections import namedtuple
import os

import yaml

from lyrics_scraping import data
from pyutils.genutils import load_yaml


# TODO: explain
_CFG_EXT = "yaml"
_LOG_CFG_FILENAME = 'logging_cfg'
_MAIN_CFG_FILENAME = 'main_cfg'
_SCHEMA_FILENAME = "music.sql"
_data_filenames = namedtuple("data_filenames", "user_cfg default_cfg schema")


def _add_data_filenames():
    """TODO
    """
    _data_filenames.user_cfg = {
        'log': '{}.'.format(_LOG_CFG_FILENAME) + _CFG_EXT,
        'main': '{}.'.format(_MAIN_CFG_FILENAME) + _CFG_EXT}
    _data_filenames.default_cfg = dict(
        [("default_" + k, "default_" + v)
         for k, v in _data_filenames.user_cfg.items()])
    _data_filenames.schema = _SCHEMA_FILENAME


_add_data_filenames()


def _get_data_dirpath():
    """TODO

    Returns
    -------

    """
    return data.__path__[0]


def add_plural_ending(obj, plural_end="s", singular_end=""):
    """Add plural ending if a number is greater than 1 or there are many
    values in a list.

    If the number is greater than one or more than one item is found in the
    list, the function returns by default 's'. If not, then the empty string is
    returned.

    Parameters
    ----------
    obj : int, float or list
        The number or list that will be checked if a plural or singular ending
        will be returned.
    plural_end : str, optional
        The plural ending (the default value is "s" which implies that "s'" will
        be returned in the case that the number is greater than 1 or the list
        contains more than one item).
    singular_end : str, optional
        The singular ending (the default value is "" which implies that an
        empty string will be returned in the case that the number is 1 or less,
        or the list contains 1 item).

    Returns
    -------
    str : "s" or ""
        "s" if number is greater than 1 or more than one item is found in the
        list, "" (empty string) otherwise.

    Raises
    ------
    TypeError
        TODO

    """
    if isinstance(obj, list):
        num = len(obj)
    else:
        if not (isinstance(obj, int) or isinstance(obj, float)):
            raise TypeError("obj must be a list, int or float")
        num = obj
    return plural_end if num > 1 else singular_end


def get_bak_cfg_filepath(cfg_type):
    """TODO

    Parameters
    ----------
    cfg_type

    Returns
    -------

    """
    valid_cfg_types = list(_data_filenames.user_cfg.keys())
    assert cfg_type in valid_cfg_types, \
        "Wrong type of data file: '{}' (choose from {})".format(
            cfg_type, ", ".join(valid_cfg_types))
    filename = '.{}_cfg.bak'.format(cfg_type)
    return os.path.join(_get_data_dirpath(), filename)


def get_data_filepath(file_type):
    """Return the path to a data file used by :mod:`lyrics_scraping`.

    The data file can either be the:

    - **default_log**: refers to the `default logging configuration file`_ used
      to setup the logging for all custom modules.
    - **default_main**: refers to the `default main configuration file`_ used to
      setup a lyrics scraper.
    - **log**: refers to the `user-defined logging configuration file`_ which is
      used to setup the logging for all custom modules.
    - **main**: refers to the `user-defined main configuration file`_ used to
      setup a lyrics scraper.
    - **schema**: refers to the `SQL schema file music.sql`_ used for creating the SQLite
      database which stores the scraped data.

    Parameters
    ----------
    file_type : str, {'default_log', 'default_main', 'log', 'main', 'schema'}
        The type of data file for which we want the path.

    Returns
    -------
    filepath : str
        The path to the data file.

    Raises
    ------
    AssertionError
        Raised if the wrong type of data file is given to the function. Only
        {'default_log', 'default_main', 'log', 'main', 'schema'} are accepted
        for `file_type`.

    """
    valid_file_types = list(_data_filenames.user_cfg.keys()) \
        + list(_data_filenames.default_cfg.keys())
    valid_file_types.append(_data_filenames.schema)
    assert file_type in valid_file_types, \
        "Wrong type of data file: '{}' (choose from {})".format(
            file_type, ", ".join(valid_file_types))
    if file_type == 'schema':
        filename = _data_filenames.schema
    elif file_type.startswith('default'):
        filename = _data_filenames.default_cfg[file_type]
    else:
        filename = _data_filenames.user_cfg[file_type]
    return os.path.join(_get_data_dirpath(), filename)


def load_cfg(cfg_type):
    """TODO

    Parameters
    ----------
    cfg_type

    Returns
    -------

    Raises
    ------

    """
    valid_cfg_types = list(_data_filenames.user_cfg.keys()) + \
        list(_data_filenames.default_cfg.keys())
    assert cfg_type in valid_cfg_types, \
        "Wrong type of data file: '{}' (choose from {})".format(
            cfg_type, ", ".join(valid_cfg_types))
    if _CFG_EXT == 'yaml':
        return load_yaml(get_data_filepath(cfg_type))
    else:
        # TODO: raise error
        print("File EXTENSION '{}' not supported".format(_CFG_EXT))
        return None


def dump_cfg(filepath, cfg_dict):
    """TODO

    Parameters
    ----------
    filepath
    cfg_dict

    Raises
    ------

    """
    if _CFG_EXT == 'yaml':
        with open(filepath, 'w') as f:
            yaml.dump(cfg_dict, f)
    else:
        # TODO: raise error
        print("File EXTENSION '{}' not supported".format(_CFG_EXT))
