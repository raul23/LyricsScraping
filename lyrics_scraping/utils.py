"""Collection of utilities specifically for the lyrics scraping project.

.. _default logging configuration file: https://bit.ly/2oPJSr4
.. _default main configuration file: https://bit.ly/2n764MV
.. _user-defined logging configuration file: https://bit.ly/2niTDgY
.. _user-defined main configuration file: https://bit.ly/2oyt0VJ
.. _SQL schema file music.sql: https://bit.ly/2kIMYvn

"""

import os
# Custom modules
from lyrics_scraping import data
from pyutils.genutils import list_to_str


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
    valid_file_types = ['default_log', 'default_main', 'log', 'main', 'schema']
    assert file_type in valid_file_types, \
        "Wrong type of data file: '{}' (choose from {})".format(
            file_type, list_to_str(valid_file_types))
    if file_type.endswith('log'):
        filename = '{}ging_cfg.yaml'.format(file_type)
    elif file_type.endswith('main'):
        filename = '{}_cfg.yaml'.format(file_type)
    else:
        filename = 'music.sql'
    return os.path.join(data.__path__[0], filename)
