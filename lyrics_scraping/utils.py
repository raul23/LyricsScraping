"""Collection of utilities specifically for the lyrics scraping project.

"""

import os
# Custom modules
from lyrics_scraping import data


def get_data_filepath(file_type, default=False):
    """Return the path to a data file used by the `lyrics_scraping` module.

    The data file can either be the:
    - SQL music schema file [1]: used for creating the SQLite database used for
                                 storing the scraped data
    - main configuration file [2] : used for configuring a lyrics scraper
    - logging configuration file [3] : used to set up the logging for all
                                       custom modules

    By setting `default` to True, you get instead the path to the configuration
    file with default values. Otherwise, you get the path to the configuration
    file currently used by the program, i.e. the one actually edited by the
    user. Note that `default` doesn't have any effect with the schema file.

    Parameters
    ----------
    file_type : str, {'log', 'main', 'schema'}
        The type of data file for which we want the path. 'log' refers to the
        logging config file, 'main' to the main config file used to setup a
        lyrics scraper, and 'schema' to the SQL music schema file.
    default : bool, optional
        Whether to get the path to the default configuration file. Note that
        `default` doesn't have any effect with the schema file.(the default
        value is False which implies that the path to the configuration file
        currently used by the program will be returned).

    Returns
    -------
    filepath : str
        The path to the data file.

    Raises
    ------
    AssertionError
        Raised if the wrong type of data file is given to the function. Only
        {'log', 'main', 'schema'} are accepted for `file_type`.

     References
     ----------
     .. [1] `TODO: add URL to SQL schema file`_.
     .. [2] `TODO: add URL to main config file`_.
     .. [3] `TODO: add URL to logging config file`_.

    """
    if file_type == "log":
        filename = 'default_logging_cfg.yaml' if default else 'logging_cfg.yaml'
    elif file_type == 'main':
        filename = 'default_main_cfg.yaml' if default else 'main_cfg.yaml'
    elif file_type == 'schema':
        filename = 'music.sql'
    else:

        raise AssertionError("Wrong type of data file: '{}' (choose from "
                             "'log', 'main', 'schema')".format(file_type))
    return os.path.join(data.__path__[0], filename)
