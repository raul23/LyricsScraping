"""TODO
"""

from pyutils.testutils import TestBase


class TestLyricsScraping(TestBase):
    # TODO
    CREATE_TEST_DATABASE = False
    ADD_FILE_HANDLER = True
    LOGGER_NAME = __name__
    LOGGING_FILENAME = "scraping.log"
    SHOW_FIRST_CHARS_IN_LOG = 1000
    SCHEMA_FILEPATH = None
    DB_FILENAME = "db.qlite"
