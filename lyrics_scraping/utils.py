"""Collection of utilities specifically for the lyrics scraping project.

.. _default logging configuration file: https://bit.ly/2oPJSr4
.. _default main configuration file: https://bit.ly/2n764MV
.. _user-defined logging configuration file: https://bit.ly/2niTDgY
.. _user-defined main configuration file: https://bit.ly/2oyt0VJ
.. _SQL schema file music.sql: https://bit.ly/2kIMYvn

"""

from collections import namedtuple
import os

from lyrics_scraping import data
from pyutils.genutils import load_yaml

# TODO: explain
_CFG_EXT = "yaml"
_data_filenames = namedtuple("data_filenames", "user_cfg default_cfg schema")


def _add_data_filenames():
    """TODO
    """
    _data_filenames.user_cfg = {'log': 'logging_cfg.' + _CFG_EXT,
                                'main': 'main_cfg.' + _CFG_EXT}
    _data_filenames.default_cfg = dict(
        [(k, "default_" + v) for k, v in _data_filenames.user_cfg.items()])
    _data_filenames.schema = "music.sql"


_add_data_filenames()


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
    valid_cfg_types = _data_filenames.user_cfg
    assert cfg_type in valid_cfg_types, \
        "Wrong type of data file: '{}' (choose from {})".format(
            cfg_type, list_to_str(valid_cfg_types))
    filename = '.{}_cfg.bak'.format(cfg_type)
    return os.path.join(get_data_dirpath(), filename)


def get_data_dirpath():
    """TODO

    Returns
    -------

    """
    return data.__path__[0]


def get_data_filepath(file_type):
    """Return the path to a data file used by the `lyrics_scraping` module.

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
    valid_file_types = _data_filenames.user_cfg + _data_filenames.default_cfg
    valid_file_types.append(_data_filenames.schema)
    assert file_type in valid_file_types, \
        "Wrong type of data file: '{}' (choose from {})".format(
            file_type, list_to_str(valid_file_types))
    if file_type == 'schema':
        filename = _data_filenames.schema
    elif file_type.startswith('default'):
        filename = _data_filenames.default_cfg[file_type]
    else:
        filename = _data_filenames.user_cfg[file_type]
    return os.path.join(get_data_dirpath(), filename)


def load_cfg(cfg_type):
    """TODO

    Parameters
    ----------
    cfg_type

    Returns
    -------

    """
    valid_file_types = _data_filenames.user_cfg + _data_filenames.default_cfg
    return load_yaml(get_data_filepath(cfg_type))



# TODO: remove this function which can be simplified to
# ", ".join(list_)
def list_to_str(list_):
    """Convert a list of strings into a single string.

    Parameters
    ----------
    list_ : list of str
        List of strings to be converted into a single string.

    Returns
    -------
    str_ : str
        The converted string.

    Examples
    --------
    >>> list_ = ['CA', 'FR', 'US']
    >>> list_to_str(list_)
    "'CA', 'FR', 'US'"
    # This function can be useful for building the WHERE condition in SQL
    # expressions:
    >>> list_countries = ['CA', 'FR', 'US']
    >>> str_countries = list_to_str(list_countries)
    >>> "SELECT * FROM table WHERE country IN ({})".format(str_countries)
    "SELECT * FROM table WHERE country IN ('CA', 'FR', 'US')"

    """
    # TODO:
    return ", ".join(map(lambda a: "'{}'".format(a), list_))
