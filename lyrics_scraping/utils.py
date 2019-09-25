"""Collection of utilities specifically for the lyrics scraping project.

"""

import os
# Custom modules
from lyrics_scraping import data


def get_config_filepath(cfg_type, default=False):
    """Return the path to a user's configuration file.

    The configuration file can either be:
    - the main configuration file [1] : used for configuring a lyrics scraper
    - the logging configuration file [2] : used to set up the logging for all
                                           custom modules

    By setting `default` to True, you get instead the path to the configuration
    file with default values. Otherwise, you get the path to the configuration
    file currently used by the program, i.e. the one actually edited by the
    user.

    Parameters
    ----------
    cfg_type : str, {'log', 'main'}
        The type of configuration file for which we want the path. 'log' refers
        to the logging config file, and 'main' to the main config file used to
        setup a lyrics scraper.

    default : bool, optional
        Whether to get the path to the default configuration file (the default
        value is False which implies that the path to the configuration file
        currently used by the program will be returned).

    Returns
    -------
    filepath : str
        The path to the configuration file.

    Raises
    ------
    AssertionError
        Raised if te wrong type of configuration file is given to the function.
        Only 'log' and 'main' are accepted for `cfg_type`.

     References
     ----------
     .. [1] `TODO: add URL to main config file`_.
     .. [2] `TODO: add URL to logging config file`_.

    """
    assert cfg_type in ['log', 'main'], "Wrong type of config file"
    if cfg_type == "log":
        filename = 'default_logging_cfg.yaml' if default else 'logging_cfg.yaml'
    else:
        filename = 'default_main_cfg.yaml' if default else 'main_cfg.yaml'
    return os.path.join(data.__path__[0], filename)
