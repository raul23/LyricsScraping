"""Module summary

Extended module summary

"""

import os
import sqlite3
# NOTES:
# * I'm using `requests` in ../save_webpages/run_saver.py
# * For urllib with Python 2, it is
# `from six.moves.urllib.parse import urlparse`
import urllib
# Third-party modules
import ipdb
# Custom modules
import scrapers.scraper_exceptions as scraper_exc
from utilities.databases.dbutils import connect_db, sql_sanity_check
import utilities.exceptions.sql as sql_exc
from utilities.logging.logutils import get_logger
from utilities.save_webpages import SaveWebpages


class LyricsScraper:
    """Base class for scraping and saving webpages locally.

    Parameters
    ----------
    main_cfg : dict
        Description
    logger : dict or LoggingWrapper
        If `logger` is a ``dict``, then a new logger will be setup for each
        module. If `logger` is a ``LoggingWrapper``, then the same logger will
        be reused throughout the modules.

    Attributes
    ----------
    main_cfg : dict
        Logging configuration ``dict``.
    logger_p : LoggingWrapper
        Description
    music_db_filepath : str
        Absolute path to music SQLite db.
    cache_filepath : str
        Absolute path to cache directory where webpages will be saved.
    lyrics_urls : list of str
        List of URLs to lyrics webpages
    music_conn : sqlite3.Connection
        SQLite database connection.
    saver : SaveWebpages
        For retrieving and saving webpage in cache.

    Methods
    -------
    start_scraping()
        Description

    """

    def __init__(self, main_cfg, logger):
        self.main_cfg = main_cfg
        self.logger_p = get_logger(__name__,
                                   __file__,
                                   os.getcwd(),
                                   logger)
        self.music_db_filepath = \
            os.path.expanduser(main_cfg['music_db_filepath'])
        self.cache_filepath = os.path.expanduser(main_cfg['cache_filepath'])
        self.lyrics_urls = main_cfg['lyrics_urls']
        self.music_conn = None
        self.saver = SaveWebpages(main_cfg=self.main_cfg,
                                  logger=logger)

    def start_scraping(self):
        """Start the web scraping of lyrics webpages.

        This is the only public method. It is where everything starts: db
        connection, processing of each lyrics URL, and catching of all
        exceptions that prevent a given URL of being processed further.

        However, all the important tasks (db connection, URL processing) are
        actually delegated to separate methods (_db_connection(),
        _process_url()).

        Notes
        ----
        Any exceptions that are not caught here are redirected to the main
        script calling this method. See for example ../script/run_scraper.py

        """
        # Connect to the music database
        self._connect_db()
        # Process list of URLs to lyrics websites
        for url in self.lyrics_urls:
            try:
                self._process_url(url)
            except urllib.error.URLError as e:
                self.logger_p.exception(e)
                self.logger_p.warning(
                    "The URL {} seems to be down!".format(url))
                self.logger_p.info("Skipping the URL {}".format(url))
            except (scraper_exc.InvalidURLDomainError,
                    scraper_exc.InvalidURLCategoryError,
                    sql_exc.SQLSanityCheckError) as e:
                self.logger_p.error(e)
                self.logger_p.info("Skipping the URL {}".format(url))
            except (scraper_exc.MultipleLyricsURLError,
                    scraper_exc.OverwriteSongError) as e:
                self.logger_p.info(e)
                self.logger_p.info("Skipping the URL {}".format(url))

    def _connect_db(self):
        """Connect to the SQLite music database.

        Raises
        ------
        sqlite3.Error
             Raised if any SQLite-related error occurs, such as IntegrityError
             or OperationalError.

        """
        # Connect to the music database
        try:
            self.logger_p.info(
                "Connecting to db '{}'".format(self.music_db_filepath))
            self.music_conn = connect_db(self.music_db_filepath)
        except sqlite3.Error as e:
            raise sqlite3.Error(e)
        else:
            self.logger_p.debug("Db connection established!")

    def _check_url_in_db(self, url):
        """Check if a lyrics URL is already present in the database.

        The first thing to do when processing a given artist or lyrics URL is
        to check if it has not already been processed previously, i.e. verify
        if the lyrics URL is already in the db. Hence, we speed up the
        program execution.

        Parameters
        ----------
        url : str
            Lyrics URL to be checked if it is already in the db.

        Raises
        ------
        MultipleLyricsURLError
            Raised if a lyrics URL was found more than once in the music db.

        OverwriteSongError
            Raised if a song was already found in the db and the db can't be
            updated because the ``overwrite_tables`` flag is disabled.

        """
        res = self._select_song(url)
        if len(res) == 1:
            self.logger_p.debug(
                "There is already a song with the same URL {}".format(url))
            if self.main_cfg['overwrite_tables']:
                self.logger_p.debug(
                    "Since the 'overwrite_tables' flag is set to True, the URL "
                    "will be processed and the music db will be updated as a "
                    "consequence")
            else:
                raise scraper_exc.OverwriteSongError(
                    "Since the 'overwrite_tables' flag is set to False, the URL "
                    "will be ignored")
        elif len(res) == 0:
            self.logger_p.debug(
                "The lyrics URL {} was not found in the music db".format(url))
        else:
            raise scraper_exc.MultipleLyricsURLError(
                "The lyrics URL {} was found more than once in the music "
                "db".format(url))

    def _scrape_artist_page(self, artist_filename, artist_url):
        """Scrape the artist webpage

        It crawls the webpage and scrapes any useful info to be inserted in the
        music database, such as

        Parameters
        ----------
        artist_filename
        artist_url

        Raises
        ------
        NotImplementedError
            Raised if the derived class didn't implement this method.

        """
        raise NotImplementedError

    def _scrape_lyrics_page(self, lyrics_filename, lyrics_url):
        """

        Parameters
        ----------
        lyrics_filename
        lyrics_url

        Raises
        ------
        NotImplementedError
            Raised if the derived class didn't implement this method.

        """
        raise NotImplementedError

    def _process_url(self, url):
        """

        Parameters
        ----------
        url

        Raises
        ------
        NotImplementedError
            Raised if the derived class didn't implement this method.

        """
        raise NotImplementedError

    def _execute_sql(self, sql, values=None):
        """

        Parameters
        ----------
        cur
        sql
        values : tuple of ?, optional

        Returns
        -------

        """
        cur = self.music_conn.cursor()
        if values is None:
            # Select query
            cur.execute(sql)
            return cur.fetchall()
        else:
            # Insert query
            try:
                sql_sanity_check(sql, values)
                cur.execute(sql, values)
            except sqlite3.IntegrityError as e:
                self.logger_p.debug(e)
                return None
            except (TypeError, AssertionError) as e:
                self.logger_p.error(e)
                raise sql_exc.SQLSanityCheckError(e)
            else:
                if not self.main_cfg['autocommit']:
                    self.music_conn.commit()
                self.logger_p.debug(
                    "Query execution successful! lastrowid={}".format(
                        cur.lastrowid))
                return cur.lastrowid

    def _insert_album(self, album):
        """Insert an info about an album in the database.

        Parameters
        ----------
        album : tuple of str
            Description

        """
        self.logger_p.debug(
            "Inserting the album: album_title={}, artist_name={}, "
            "year={}".format(album[0], album[1], album[2]))
        sql = "INSERT INTO albums (album_title, artist_name, year) " \
              "VALUES (?, ?, ?)"
        self._execute_sql(sql, album)

    def _insert_artist(self, artist_name):
        """

        Parameters
        ----------
        artist_name : tuple of str
            Description

        """
        self.logger_p.debug("Inserting the artist: {}".format(artist_name[0]))
        sql = '''INSERT INTO artists (artist_name) VALUES (?)'''
        self._execute_sql(sql, artist_name)

    def _insert_song(self, song):
        """

        Parameters
        ----------
        song : tuple of str
            Description

        """
        self.logger_p.debug(
            "Inserting the song: song_title={}, artist_name={}, "
            "album_title={}".format(song[0], song[1], song[4]))
        sql = "INSERT INTO songs (song_title, artist_name, lyrics, " \
              "lyrics_url, album_title, year) VALUES (?, ?, ?, ?, ?, ?)"
        self._execute_sql(sql, song)

    def _select_song(self, lyrics_url):
        """

        Parameters
        ----------
        lyrics_url : str
            Description

        Returns
        -------

        """
        self.logger_p.debug(
            "Selecting the song where lyrics_url={}".format(lyrics_url))
        sql = "SELECT * FROM songs WHERE lyrics_url='{}'".format(
            lyrics_url)
        return self._execute_sql(sql)
