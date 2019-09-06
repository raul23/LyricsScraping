"""Module that defines the base class for scraping lyrics websites.

More specifically, the derived classes (e.g. ``AZLyricsScraper``) are the ones
that do the actual scraping of the lyrics webpages.

The base class ``LyricsScraper`` is responsible of connecting to the music
database and thus accessing the database for data retrieval (SELECT) and
updating (INSERT).

See the structure of the music database as defined in the
`music.sql schema
<https://github.com/raul23/lyrics-scraper/blob/master/database/music.sql/>`_.

"""

import os
import sqlite3
# NOTES:
# * I'm using `requests` in ../save_webpages/run_saver.py
# * For urllib with Python 2, it is
# `from six.moves.urllib.parse import urlparse`
import urllib
# Custom modules
import utils.exceptions.connection as connec_exc
import utils.exceptions.files as files_exc
import utils.exceptions.sql as sql_exc
import scrapers.scraper_exceptions as scraper_exc
from utils.databases.dbutils import connect_db, sql_sanity_check
from utils.logging.logutils import get_logger
from utils.save_webpages import SaveWebpages


class LyricsScraper:
    """Base class for scraping and saving webpages locally.

    Parameters
    ----------
    main_cfg : dict
        Main configuration dictionary that defines among other important
        options, the list of URLs to be processed and the path to the cache
        directory. See the content of the config dict as defined in
        `main_cfg.yaml <https://bit.ly/2m27NSI/>`_.
    logger : dict or LoggingWrapper
        If `logger` is a ``dict``, then a new logger will be setup for each
        module. If `logger` is a ``LoggingWrapper``, then the same logger will
        be reused throughout the modules.

    Attributes
    ----------
    main_cfg : dict
        Logging configuration ``dict``.
    logger_p : LoggingWrapper
        Logger for logging to console and file, at the same time.
    music_db_filepath : str
        File path to the SQLite music database.
    cache_filepath : str
        File path to the cache directory where webpages are saved.
    lyrics_urls : list of str
        List of URLs to lyrics webpages.
    music_conn : sqlite3.Connection
        SQLite database connection.
    saver : SaveWebpages
        For retrieving and saving webpage in cache.

    Methods
    -------
    start_scraping()
        Start the web scraping of the lyrics website.

    Notes
    -----
    `logger_p` is a logger that is associated with the base class
    ``LyricsScraper``. The derive classes, such as ``AzlyricsScraper``, have
    their own logger. Hence, we can differentiate whose logs belong to what
    class, when reading the log file.

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
        """Start the web scraping of the lyrics website.

        This is the only public method. It is where everything starts: db
        connection, processing of each lyrics URL, and catching of all
        exceptions that prevent a given URL of being processed further.

        However, all the important tasks (db connection, URL processing) are
        actually delegated to separate methods (_db_connection(),
        _process_url()).

        Notes
        -----
        Any exceptions that are not caught here are redirected to the main
        script calling this method. See for example ../script/run_scraper.py

        """
        # Connect to the music database
        self._connect_db()
        # Process list of URLs to lyrics websites
        for url in self.lyrics_urls:
            try:
                self._process_url(url)
            except OSError as e:
                self.logger_p.exception(e)
                self.logger_p.info("Skipping the URL {}".format(url))
            except urllib.error.URLError as e:
                self.logger_p.exception(e)
                self.logger_p.warning(
                    "The URL {} seems to be down!".format(url))
                self.logger_p.info("Skipping the URL {}".format(url))
            except (connec_exc.HTTP404Error,
                    files_exc.OverwriteFileError,
                    scraper_exc.InvalidURLDomainError,
                    scraper_exc.InvalidURLCategoryError,
                    scraper_exc.MultipleLyricsURLError,
                    sql_exc.SQLSanityCheckError) as e:
                self.logger_p.error(e)
                self.logger_p.info("Skipping the URL {}".format(url))
            except scraper_exc.OverwriteSongError as e:
                self.logger_p.info(e)
                self.logger_p.info("Skipping the URL {}".format(url))

    def _connect_db(self):
        """Connect to the SQLite music database.

        The SQLite music database is used for saving any relevant data from the
        scraped webpages.

        See the structure of the music database as defined in the `music.sql
        schema <https://bit.ly/2lGbeOw/>`_.

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
            This is a custom exception
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

    def _scrape_artist_page(self, artist_filepath, artist_url):
        """Scrape the artist webpage.

        This method should scrape the artist webpage for useful data to be
        added in the database, such as the artist's name.

        This method needs to be implemented by the derived class. If it's not,
        then an ``NotImplementedError`` exception is raised.

        Parameters
        ----------
        artist_filepath : str
            The file path of the artist webpage that will be scraped. The file
            path will be used to save the HTML document in cache.
        artist_url : str
            URL to the artist webpage that will be scraped.

        Raises
        ------
        NotImplementedError
            Raised if the method is not implemented by the derived class.

        See Also
        --------
        azlyrics_scraper._scrape_artist_page : an example of an implemented
                                               method.

        Notes
        -----
        Not all lyrics websites will have an artist webpage, on top of the
        lyrics webpage. `www.azlyrics.com <https://www.azlyrics.com/>`_ has an
        artist webpage, along with a lyrics webpage.

        """
        # TODO: add error message like NotImplementedError("blabla")
        raise NotImplementedError

    def _scrape_lyrics_page(self, lyrics_filename, lyrics_url):
        """Scrape the lyrics webpage.

        This method should scrape the lyrics webpage for useful data to be
        added in the database, such as the song's title and the lyrics text.

        This method needs to be implemented by the derived class. If it's not,
        then an ``NotImplementedError`` exception is raised.

        Parameters
        ----------
        lyrics_filename : str
            Filename of the lyrics webpage that is being scraped. The filename
            will be used to save the HTML document in cache.
        lyrics_url : str
            URL to the lyrics webpage that is being scraped.

        Raises
        ------
        NotImplementedError
            Raised if the method is not implemented by the derived class.

        See Also
        --------
        azlyrics_scraper._scrape_lyrics_page : an example of an implemented
                                               method.

        """
        # TODO: add error message like NotImplementedError("blabla")
        raise NotImplementedError

    def _process_url(self, url):
        """Process each URL defined in the YAML config file.

        Depending on the lyrics website, the URLs can refer to an artist or
        lyrics webpage.

        This method needs to be implemented by the derived class. If it's not,
        then an ``NotImplementedError`` exception is raised.

        Parameters
        ----------
        url : str
            URL to the artist's or lyrics webpage that will be scraped.

        Raises
        ------
        NotImplementedError
            Raised if the method is not implemented by the derived class.

        See Also
        --------
        azlyrics_scraper._process_url : an example of an implemented method.

        """
        # TODO: add error message like NotImplementedError("blabla")
        raise NotImplementedError

    def _execute_sql(self, sql, values=None):
        """Execute an SQL expression.

        The SQL expression can be a SELECT or INSERT query.

        `values` is needed only in the case of an INSERT query since we are
        inserting data into the db, unlike a SELECT query which only retrieve
        data from the db.

        See the structure of the music database as defined in the `music.sql
        schema <https://bit.ly/2lGbeOw/>`_.

        Parameters
        ----------
        sql : str
            SQL query to be executed.
        values : tuple of str, optional
            The values to be inserted in the database (the default is None,
            which implies that the SQL query is a SELECT expression).

        Returns
        -------
        cur.fetchall() : list of tuple
            List of tuple from the executed SELECT query, where each tuple
            represents one row entry [1].

            IMPORTANT: this returned value only happens with SELECT queries.
        None
            Returned if the table couldn't be updated because of an
            sqlite3.IntegrityError exception.

            IMPORTANT: this returned value only happens with INSERT queries.

            It is not a fatal exception that should stop the program execution
            since the exception can occur when the data to be inserted is
            already in the database which is a common case (e.g. if we re-run
            the program multiple times, we will catch this exception). If this
            case happens, we only skip the URL and process the next URL in the
            list.
        lastrowid : int
            The id of the last row in the updated table, after the insertion
            was successful.

            IMPORTANT: this returned value only happens with INSERT queries.

        Raises
        ------
        SQLSanityCheckError
            Raised if the sanity check on the SQL query failed, e.g. the
            query's values are not of ``tuple`` type or wrong number of values
            in the SQL query.

            This is a custom exception.

        Notes
        -----
        The returned value (i.e. the `lastrowid`) when executing an INSERT
        query is not used within the respective INSERT methods, e.g.
        _insert_album().

        References
        ----------
        .. [1] `A thorough guide to SQLite database operations in Python
        <https://bit.ly/2xYreie/>`_.

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
                # TODO: explain why this error is only logged as a debug
                self.logger_p.debug(e)
                return None
            except sql_exc.SQLSanityCheckError as e:
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
        """Insert data about an album in the database.

        Data about an album can consist in the album' title and the year the
        album was published.

        See the `albums` table as defined in the `music.sql schema
        <https://bit.ly/2lGbeOw/>`_.

        Parameters
        ----------
        album : tuple of str
            The tuple contains the relevant data about an album that will be
            added to the database, such as the album title, the artist name, and
            the year the album was published.

        """
        self.logger_p.debug(
            "Inserting the album: album_title={}, artist_name={}, "
            "year={}".format(album[0], album[1], album[2]))
        sql = "INSERT INTO albums (album_title, artist_name, year) " \
              "VALUES (?, ?, ?)"
        self._execute_sql(sql, album)

    def _insert_artist(self, artist_name):
        """Insert an artist's name in the database.

        An artist's name can refer to a group or an individual (solo).

        See the `artists` table as defined in the `music.sql schema
        <https://bit.ly/2lGbeOw/>`_.

        Parameters
        ----------
        artist_name : tuple of str
            The tuple contains the name of the artist that will be added to the
            database.

        """
        self.logger_p.debug("Inserting the artist: {}".format(artist_name[0]))
        sql = '''INSERT INTO artists (artist_name) VALUES (?)'''
        self._execute_sql(sql, artist_name)

    def _insert_song(self, song):
        """Insert data about a song in the database.

        The data about a song that will be added to the database can consist to
        the song title, artist name, and album title.

        See the `songs` table as defined in the `music.sql schema
        <https://bit.ly/2lGbeOw/>`_.

        Parameters
        ----------
        song : tuple of str
            The tuple contains the relevant data about a song that will be
            added to the database, such as the song title, the artist name, and
            the lyrics text.

        """
        self.logger_p.debug(
            "Inserting the song: song_title={}, artist_name={}, "
            "album_title={}".format(song[0], song[1], song[4]))
        sql = "INSERT INTO songs (song_title, artist_name, lyrics, " \
              "lyrics_url, album_title, year) VALUES (?, ?, ?, ?, ?, ?)"
        self._execute_sql(sql, song)

    def _select_song(self, lyrics_url):
        """Select a song from the database based on a lyrics URL.

        The lyrics URL is used as the WHERE condition to be used for retrieving
        the associated song from the database.

        See the `songs` table as defined in the `music.sql schema
        <https://bit.ly/2lGbeOw/>`_.

        Parameters
        ----------
        lyrics_url : str
            Lyrics URL to be used in the WHERE condition of the SELECT query.

        Returns
        -------
        cur.fetchall() : list of tuple
            List of tuple from the executed SELECT query, where each tuple
            represents one row entry [1].

        """
        self.logger_p.debug(
            "Selecting the song where lyrics_url={}".format(lyrics_url))
        sql = "SELECT * FROM songs WHERE lyrics_url='{}'".format(
            lyrics_url)
        return self._execute_sql(sql)
