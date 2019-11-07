"""Module that defines tests for :mod:`~lyrics_scraping.scrapers.azlyrics_scraper`
"""

import logging
import os
import sqlite3
import unittest
from logging import NullHandler

from .utils import TestLyricsScraping
from lyrics_scraping.scrapers import lyrics_scraper
from lyrics_scraping.scrapers import azlyrics_scraper
from lyrics_scraping.scrapers.azlyrics_scraper import AZLyricsScraper
from lyrics_scraping.utils import load_cfg
from pyutils.genutils import get_qualname
from pyutils.logutils import setup_logging_from_cfg

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class TestScrapingScript(TestLyricsScraping):
    # TODO
    TEST_MODULE_QUALNAME = get_qualname(azlyrics_scraper)
    LOGGER_NAME = __name__
    SHOW_FIRST_CHARS_IN_LOG = 0

    @classmethod
    def setUpClass(cls):
        """TODO
        """
        super().setUpClass()
        # We will take charge of setting logging for lyrics_scraper and cie
        lyrics_scraper._SETUP_LOGGING = False
        # Load logging config
        logging_cfg = load_cfg("log")
        # Disable add_datetime
        logging_cfg['add_datetime'] = False
        # Change console handler's level to DEBUG
        logging_cfg['handlers']['console']['level'] = "DEBUG"
        # Change console handler's formatter to 'console'
        logging_cfg['handlers']['console']['formatter'] = "console"
        # Update file handler's filename our test logger's filename
        logging_cfg['handlers']['file']['filename'] = cls.log_filepath
        # Add file handlers to all loggers
        for log_name, log_attrs in logging_cfg['loggers'].items():
            log_attrs['handlers'].append('file')
        # IMPORTANT: remove the root logger because if we don't our test logger
        # will be setup as the root logger in the logging config file
        del logging_cfg['root']
        # Force custom modules to use a different logger with a shorter name
        azlyrics_scraper.logger = logging.getLogger("scraper")
        lyrics_scraper.logger = logging.getLogger("scraper")
        # Setup logging for all custom modules based on updated logging config
        # dict
        setup_logging_from_cfg(logging_cfg)

    @unittest.skip("test_get_lyrics_from_album_case_1()")
    def test_get_lyrics_from_album_case_1(self):
        """TODO
        Good album title only
        One choice only
        """
        # TODO: explain
        init_params = {}
        meth_params = {"album_title": "Speak & Spell"}
        expected_nb_songs = 13
        extra_msg = "- Only a <color>valid album title</color> is given"
        bulk_lyrics = self._test_get_lyrics(init_params, meth_params, extra_msg)
        self.check_bulk_lyrics(bulk_lyrics, meth_params, expected_nb_songs)

    @unittest.skip("test_get_lyrics_from_album_case_2()")
    def test_get_lyrics_from_album_case_2(self):
        """TODO
        Good album title only and max_songs=5
        One choice only
        """
        # TODO: explain
        init_params = {}
        meth_params = {"album_title": "Music For The Masses",
                       "max_songs": 5}
        extra_msg = "- Only a <color>valid album title</color> is given"
        extra_msg += "\n- <color>Max songs</color> is 5"
        bulk_lyrics = self._test_get_lyrics(init_params, meth_params, extra_msg)
        self.check_bulk_lyrics(bulk_lyrics, meth_params,
                               meth_params['max_songs'])

    @unittest.skip("test_get_lyrics_from_album_case_3()")
    def test_get_lyrics_from_album_case_3(self):
        """TODO
        Both good album title and artist name
        Many choices but incorrect search result selected

        TODO: Another test to remember is with My New Moon and 17 songs
        No 'other songs' in the artist's webpage
        """
        # TODO: explain
        init_params = {}
        meth_params = {"album_title": "Spirit",
                       "artist_name": "Depeche Mode"}
        extra_msg = "- <color>Both valid</color> album title and artist name " \
                    "are given"
        extra_msg += "\n- <color>Incorrect search result will be selected" \
                     "</color>"
        bulk_lyrics = self._test_get_lyrics(init_params, meth_params, extra_msg)
        # Only the album should be the same but the artist different
        self.check_bulk_lyrics(bulk_lyrics, {"album_title": "Spirit"},
                               which_assert="assertTrue", log_final_msg=False)
        self.check_bulk_lyrics(bulk_lyrics, {"artist_name": "Depeche Mode"},
                               which_assert="assertFalse")

    @unittest.skip("test_get_lyrics_from_album_case_4()")
    def test_get_lyrics_from_album_case_4(self):
        """TODO
        Both good album title and artist name, and best_match=True

        TODO: Another test to remember is with My New Moon and 17 songs
        No 'other songs' in the artist's webpage
        """
        # TODO: explain
        init_params = {"best_match": True}
        meth_params = {"album_title": "Spirit",
                       "artist_name": "Depeche Mode"}
        expected_nb_songs = 14
        extra_msg = "- <color>Both valid</color> album title and artist name " \
                    "are given"
        bulk_lyrics = self._test_get_lyrics(init_params, meth_params, extra_msg)
        self.check_bulk_lyrics(bulk_lyrics, meth_params, expected_nb_songs,
                               log_lyrics_msg=True)

    @unittest.skip("test_get_lyrics_from_artist_case_1()")
    def test_get_lyrics_from_artist_case_1(self):
        """Test get_lyrics_from_album() TODO: ...
        max_songs
        random
        year_after and year_before
        """
        # TODO: explain
        init_params = {}
        meth_params = {"artist_name": "Depeche Mode",
                       "max_songs": 50,
                       "year_after": 1985,
                       "year_before": 2005,
                       "choose_random": True}
        extra_msg = "- A <color>valid artist name</color> is given"
        songs = self._test_get_lyrics(init_params, meth_params, extra_msg)
        self.check_bulk_lyrics(songs, meth_params,
                               expected_nb_songs=meth_params['max_songs'])

    # @unittest.skip("test_get_lyrics_from_artist_case_2()")
    def test_get_lyrics_from_artist_case_2(self):
        """Test get_lyrics_from_album() TODO: ...
        max_songs > number of songs from artist
        max_songs first songs
        No year_before and year_after
        """
        # TODO: explain
        init_params = {}
        meth_params = {"artist_name": "Depeche Mode",
                       "max_songs": 5000}
        extra_msg = "- A <color>valid artist name</color> is given"
        songs = self._test_get_lyrics(init_params, meth_params, extra_msg)
        self.check_bulk_lyrics(songs, meth_params)

    @unittest.skip("test_get_song_lyrics_case_1()")
    def test_get_song_lyrics_case_1(self):
        """Test get_song_lyrics() TODO: ...
        Good song title only
        """
        # TODO: explain
        init_params = {}
        get_song_params = {"song_title": "Dreaming of Me"}
        extra_msg = "- Only a <color>valid song title</color> is given"
        lyrics = self._test_get_lyrics(init_params, get_song_params, extra_msg)
        self.check_lyrics_attrs(lyrics)

    @unittest.skip("test_get_song_lyrics_case_2()")
    def test_get_song_lyrics_case_2(self):
        """Test get_song_lyrics() TODO: ...
        Good song title and artist name
        """
        # TODO: explain
        init_params = {}
        get_song_params = {"song_title": "Dreaming of Me",
                           "artist_name": "Depeche Mode"}
        extra_msg = "- <color>Both valid</color> song title and artist name " \
                    "are given"
        lyrics = self._test_get_lyrics(init_params, get_song_params, extra_msg)
        self.check_lyrics_attrs(lyrics)

    @unittest.skip("test_get_song_lyrics_case_3()")
    def test_get_song_lyrics_case_3(self):
        """Test get_song_lyrics() TODO: ...
        Good song title but misspelling artist name and best_match=True
        """
        # TODO: explain
        init_params = {"best_match": True}
        get_song_params = {"song_title": "Dream of Me",
                           "artist_name": "Allison Crauss"}
        extra_msg = "- Good song title but <color>misspelled artist " \
                    "name</color>"
        lyrics = self._test_get_lyrics(init_params, get_song_params, extra_msg)
        self.check_lyrics_attrs(lyrics)

    @unittest.skip("test_get_song_lyrics_case_4()")
    def test_get_song_lyrics_case_4(self):
        """Test get_song_lyrics() TODO: ...
        Misspelling song title but good artist name and best_match=True
        """
        # TODO: explain
        init_params = {"best_match": True}
        get_song_params = {"song_title": "Dreming of Me",
                           "artist_name": "Depeche Mode"}
        extra_msg = "- <color>Misspelled song title</color> and good " \
                    "artist name"
        lyrics = self._test_get_lyrics(init_params, get_song_params, extra_msg)
        self.check_lyrics_attrs(lyrics, which_assert="assertIsNone")

    @unittest.skip("test_get_song_lyrics_case_5()")
    def test_get_song_lyrics_case_5(self):
        """Test get_song_lyrics() TODO: ...
        Misspelling song title but good artist name and best_match=True
        """
        # TODO: explain
        init_params = {"best_match": True}
        get_song_params = {"song_title": "Deaming of Me",
                           "artist_name": "Depache Mode"}
        extra_msg = "- <color>Misspelled both</color> song title and " \
                    "artist name"
        lyrics = self._test_get_lyrics(init_params, get_song_params,
                                            extra_msg)
        self.check_lyrics_attrs(lyrics, which_assert="assertIsNone")

    @unittest.skip("test_get_song_lyrics_case_6()")
    def test_get_song_lyrics_case_6(self):
        """Test get_song_lyrics() TODO: ...
        Good song title but misspelling artist name and best_match=False
        Similar to case 3 but best_match=False
        """
        # TODO: explain
        init_params = {"best_match": False}
        get_song_params = {"song_title": "Dream of Me",
                           "artist_name": "Allison Crauss"}
        extra_msg = "- Good song title but <color>misspelled artist " \
                    "name</color>"
        lyrics = self._test_get_lyrics(init_params, get_song_params, extra_msg)
        self.check_lyrics_attrs(lyrics, get_song_params,
                                which_assert="assertFalse")

    @unittest.skip("test_get_song_lyrics_case_7()")
    def test_get_song_lyrics_case_7(self):
        """Test get_song_lyrics() TODO: ...
        Misspelling song title but good artist name and best_match=False
        Similar to case 4 but best_match=False
        """
        # TODO: explain
        init_params = {"best_match": False}
        get_song_params = {"song_title": "Dreming of Me",
                           "artist_name": "Depeche Mode"}
        extra_msg = "- <color>Misspelled song title</color> and good " \
                    "artist name"
        lyrics = self._test_get_lyrics(init_params, get_song_params, extra_msg)
        self.check_lyrics_attrs(lyrics, get_song_params,
                                which_assert="assertFalse")

    @unittest.skip("test_get_song_lyrics_case_8()")
    def test_get_song_lyrics_case_8(self):
        """Test get_song_lyrics() TODO: ...
        Misspelling song title but good artist name and best_match=False
        Similar to case 5 but best_match=False
        """
        # TODO: explain
        init_params = {"best_match": False}
        get_song_params = {"song_title": "Deaming of Me",
                           "artist_name": "Depache Mode"}
        extra_msg = "- <color>Misspelled both</color> song title and " \
                    "artist name"
        lyrics = self._test_get_lyrics(init_params, get_song_params, extra_msg)
        self.check_lyrics_attrs(lyrics, which_assert="assertIsNone")

    @unittest.skip("test_init_case_1()")
    def test_init_case_1(self):
        """Test __init__() with default values as its arguments.

        Case 1 simply tests
        :meth:`~lyrics_scraping.scrapers.AZLyricsScraper.__init__` with default
        values as its arguments, nothing is passed to the constructor.

        Thus, no database will be created and the logging setup is not performed
        since it was already done in :meth:`setUpClass`.

        """
        init_params = {}
        extra_msg = "- <color>Default values used</color>"
        self._test_init(init_params, extra_msg)
        _, meth_name = self.parse_test_method_name()

    @unittest.skip("test_init_case_2()")
    def test_init_case_2(self):
        """Test that __init__() can create a SQLite database and connect to it.

        Case 2 tests
        :meth:`~lyrics_scraping.scrapers.AZLyricsScraper.__init__` TODO:...

        """
        # TODO: explain
        extra_msg = "- Database creation"
        db_filepath = os.path.join(self.sandbox_tmpdir, "music.sqlite")
        init_params = {"db_filepath": db_filepath}
        try:
            self._test_init(init_params, extra_msg)
        except (IOError, sqlite3.OperationalError) as e:
            self.log_signs()
            logger.exception("<color>{}</color>".format(e))
            self.fail("Couldn't connect to the database")
        else:
            logger.info("<color>Connection</color> to the SQLite database could "
                        "be <color>established</color>")

    @unittest.skip("test_init_case_3()")
    def test_init_case_3(self):
        """Test that __init__() TODO:...

        Case 3 tests
        :meth:`~lyrics_scraping.scrapers.AZLyricsScraper.__init__` ...

        """
        extra_msg = "- Testing webcase"
        init_params = {"cache_dirpath": self.sandbox_tmpdir}
        scraper = self._test_init(init_params, extra_msg)
        logger.info("Sending two successive HTTP requests with the same URL ...")
        # Send fist HTTP request
        test_url = "https://en.wikipedia.org/wiki/Computer_programming"
        self.call_func(scraper.webcache.get_webpage, test_url)
        # Check that the URL was not taken from cache
        assert_msg = "The first request used cache"
        self.assertFalse(scraper.webcache.response.from_cache, assert_msg)
        logger.info("First HTTP request didn't use cache <color>as expected"
                    "</color>")
        # Send second HTTP request (same URL)
        self.call_func(scraper.webcache.get_webpage, test_url)
        # Check that the URL was taken this second time from cache
        assert_msg = "The second request didn't use cache"
        self.assertTrue(scraper.webcache.response.from_cache, assert_msg)
        logger.info("Second HTTP request used cache <color>as expected</color>")

    def check_bulk_lyrics(self, bulk_lyrics, meth_params=None,
                          expected_nb_songs=None, which_assert="assertTrue",
                          log_lyrics_msg=False, log_final_msg=True):
        """TODO

        Parameters
        ----------
        bulk_lyrics
        meth_params
        expected_nb_songs
        which_assert
        log_lyrics_msg
        log_final_msg

        """
        # TODO: explain
        # NOTE: songs can be extracted from artists or albums
        if expected_nb_songs:
            assert_msg = "There are supposed to be {} songs extracted: {} songs " \
                         "found instead".format(
                          expected_nb_songs, len(bulk_lyrics))
            self.assertTrue(len(bulk_lyrics) == expected_nb_songs, assert_msg)
        for i, lyrics in enumerate(bulk_lyrics, start=1):
            if log_lyrics_msg:
                logger.info("Checking lyrics #{}".format(i))
            self.check_lyrics_attrs(lyrics, meth_params, which_assert,
                                    log_lyrics_msg)
            if log_lyrics_msg:
                logger.info("")
        if log_final_msg:
            logger.info(
                "<color>All {}songs</color> were <color>successfully extracted"
                "</color>".format(
                 str(expected_nb_songs) + " " if expected_nb_songs else ""))

    def check_lyrics_attrs(self, lyrics, attrs_to_check=None,
                           which_assert="assertTrue", log_lyrics_msg=True):
        """TODO

        Parameters
        ----------
        lyrics
        attrs_to_check
        which_assert
        log_lyrics_msg

        Returns
        -------

        """
        assert which_assert in ["assertTrue", "assertFalse", "assertIsNone"]
        if which_assert == "assertIsNone":
            assert_msg = "The returned value should be None"
            self.assertIsNone(lyrics, assert_msg)
            logger.info("The <color>song</color> couldn't be processed "
                        "<color>as expected</color>")
        else:
            assert_method = self.__getattribute__(which_assert)
            for attr_name, attr_value in lyrics.__dict__.items():
                assert_msg = "{} not found".format(attr_name)
                self.assertTrue(attr_value, assert_msg)
                if attrs_to_check and attrs_to_check.get(attr_name):
                    if which_assert == "assertTrue":
                        assert_msg = "{} should be '{}' (not '{}')".format(
                            attr_name, attrs_to_check.get(attr_name), attr_value)
                    else:
                        assert_msg = "{} shouldn't be '{}'".format(
                            attr_name, attrs_to_check.get(attr_name))
                    assert_method(attr_value == attrs_to_check.get(attr_name),
                                  assert_msg)
            if log_lyrics_msg:
                logger.info("The <color>song</color> for <color>'{}' (by {})"
                            "</color> was <color>successfully processed"
                            "</color>".format(lyrics.song_title, lyrics.artist_name))

    def _test_get_lyrics(self, init_params, meth_params, extra_msg=None):
        """TODO

        Parameters
        ----------
        init_params
        meth_params
        extra_msg

        Returns
        -------

        """
        # TODO: explain
        if init_params.get('best_match'):
            extra_msg += "\n- The <color>best search result</color> will be " \
                         "selected"
        else:
            extra_msg += "\n- The <color>first search result</color> will be " \
                         "selected"
        _, meth_name = self.parse_test_method_name()
        funcs_and_params = [(AZLyricsScraper.__name__, init_params),
                            (meth_name, meth_params)]
        self.prepare_call_func(funcs_and_params, extra_msg)
        scraper = self.call_func(AZLyricsScraper, **init_params)
        bound_method = scraper.__getattribute__(meth_name)
        return self.call_func(func=bound_method, **meth_params)

    def _test_init(self, init_params, extra_msg=None):
        """TODO

        Parameters
        ----------
        init_params
        extra_msg

        Returns
        -------

        """
        # TODO: explain
        _, meth_name = self.parse_test_method_name()
        funcs_and_params = [(AZLyricsScraper.__name__, init_params)]
        self.prepare_call_func(funcs_and_params, extra_msg)
        scraper = self.call_func(AZLyricsScraper, **init_params)
        logger.info("<color>{}()</color> was called <color>successfully"
                    "</color>".format(AZLyricsScraper.__name__))
        return scraper
