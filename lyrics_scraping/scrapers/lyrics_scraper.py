"""Module that defines the base class for scraping lyrics websites and saving
the scraped content.

More specifically, the derived classes (e.g.
:class:`~scrapers.azlyrics_scraper.AZLyricsScraper`) are the ones that do the
actual scraping of the lyrics webpages.

By default, the scraped data is saved in a dictionary (see the variable
:data:`~LyricsScraper.scraped_data`).

The scraped data can also be saved in a database if a path to the SQLite
database is given via the argument :ref:`db_filepath
<LyricsScraperParametersLabel>`.

See the structure of the music database as defined in the `music.sql schema`_.

.. _guide: <https://bit.ly/2xYreie
.. _HTTP GET request: https://www.webopedia.com/TERM/H/HTTP_request_header.html
.. _music.sql schema: https://bit.ly/2kIMYvn
.. _saveutils.py: https://bit.ly/2m5z46A
.. _scraper.py: https://bit.ly/2msZDTC
.. _use a specialized library: https://stackoverflow.com/a/56476496
.. _YAML logging file: https://bit.ly/2m5wjSM

"""

import logging
import os
import sqlite3
# NOTES:
# * I'm using requests in ../save_webpages/run_saver.py
# * For urllib with Python 2, it is
# from six.moves.urllib.parse import urlparse
import urllib
from urllib.request import urlopen
from urllib.parse import urlparse
from logging import NullHandler
# Custom modules
import pyutils.exceptions.connection as connec_exc
import pyutils.exceptions.files as files_exc
import pyutils.exceptions.sql as sql_exc
import lyrics_scraping.scrapers.scraper_exceptions as scraper_exc
from lyrics_scraping.utils import get_data_filepath
from pyutils.dbutils import connect_db, create_db, sql_sanity_check
from pyutils.genutils import add_plural_ending, create_directory
from pyutils.logutils import get_error_msg, setup_logging
from pyutils.saveutils import SaveWebpages


logging.getLogger(__name__).addHandler(NullHandler())


class LyricsScraper:
    """Base class for scraping and saving webpages locally.

    This class is responsible for doing lots of configuration before the web
    scraping starts, such as setting up logging and the database.

    The actual scraping of the lyrics websites is done by the derived classes
    (e.g. :class:`~scrapers.azlyrics_scraper.AZLyricsScraper`) since each lyrics
    websites have their own way of being crawled (they are all designed
    differently). However, the base class is responsible for saving the scraped
    data in a dictionary (:data:`~LyricsScraper.scraped_data`) and in a database
    (if it was initially make configured).

    .. _LyricsScraperParametersLabel:

    Parameters
    ----------
    lyrics_urls : list [str]
        List of URLs to lyrics webpages which will be scraped.
    db_filepath : str, optional
        File path to the SQLite music database (the default value is an empty
        string which implies that no database will be used. The scraped data
        will be saved only in the :data:`~LyricsScraper.scraped_data`
        dictionary).
    autocommit : bool, optional
        Whether the changes to the database are committed right away (the
        default is False which implies that the changes won't take effect
        immediately).
    overwrite_db : bool, optional
        Whether the database will be overwritten. The user is given some time
        to stop the script before the database is overwritten (the default
        value is False).
    update_tables : bool, optional
        Whether the tables in the database can be updated (the default value is
        False).
    cache_dirpath : str, optional
        Path to the cache directory where webpages are saved (the default value
        is the empty string which implies that the cache will not be used).
    overwrite_webpages : bool, optional
        Whether the webpages saved in cache can be overwritten (the default value
        is False).
    http_get_timeout : int, optional
        Timeout when a GET request doesn't receive any response from the server.
        After the timeout expires, the GET request is dropped (the default
        value is 5 seconds).
    delay_between_requests : int, optional
        A delay will be added between HTTP requests in order to reduce the
        workload on the server (the default value is 8 seconds which implies
        that there will be a delay of 8 seconds between successive HTTP
        requests).
    headers : dict, optional
        The information added to the `HTTP GET request`_ that a user's browser
        sends to a Web server containing the details of what the browser wants
        and will accept back from the server. (the default value is defined
        in `saveutils.py`_).
    use_logging : bool, optional
        Whether to log messages on console and file. The logging is setup
        according to the `YAML logging file`_ (the default value is False which
        implies that no logging will be used and thus no messages will be
        printed on the console).
    **kwargs : dict
        TODO

    Attributes
    ----------
    skipped_urls : dict [str, str]
        Stores the URLs that were skipped because of an error such as
        :exc:`OSError` or :exc:`~pyutils.exceptions.connection.HTTP404Error`,
        along with the error message. The keys are the URLs and the values are
        the associated error messages.
        TODO: add link to HTTP404Error custom exception
    good_urls : set
        Stores the unique URLs that were successfully processed and saved.
    checked_urls : set
        Stores the unique URLs that were processed (whether successfully or
        unsuccessfully) during the current session.  Thus, `checked_urls` should
        equal to `skipped_urls` + `good_urls`.
    logger_p : logging.Logger
        Logger for logging to console and file.
    db_conn : sqlite3.Connection
        SQLite database connection.
    saver : SaveWebpages
        For retrieving webpages and saving them in cache. See `saveutils.py`_.
        TODO: add link to SaveWebpages type
    valid_domains : list
        Only URLs from these domains will be processed.
    logging_filepath : str
        Path to the `YAML logging file`_ which is used to setup logging for all
        custom modules.
    schema_filepath : str
        Path to `music.sql schema`_ for the music database.
    scraped_data : dict
        The scraped data is saved as a dictionary. Its structure is based on
        the database's `music.sql schema`_.

    Notes
    -----
    If the corresponding flags are activated, logging and database are setup in
    :meth:`__init__`.

    By default, the scraped data is saved in a dictionary whose structure is
    described below (see :data:`~LyricsScraper.scraped_data`). The scraped data
    will also be saved if a database is given via `db_filepath`.

    See the structure of the music database as defined in the `music.sql
    schema`_.

    The scraped webpages can also be cached in order to reduce the number of
    HTTP requests to the server (See :ref:`db_filepath
    <LyricsScraperParametersLabel>`).

    `logger_p` is a logger that is associated with the base class
    :class:`LyricsScraper`. The derive classes, such as
    :class:`~scrapers.azlyrics_scraper.AZLyricsScraper`, have their own logger.
    Hence, we can differentiate whose logs belong to what module, when reading
    the log file.

    """

    valid_domains = ["www.azlyrics.com"]
    logging_filepath = get_data_filepath(file_type='log')
    schema_filepath = get_data_filepath(file_type='schema')
    scraped_data = {
        'albums':
            {'headers': ('album_title', 'artist_name', 'year',),
             'data': []},
        'artists':
            {'headers': ('artist_name',),
             'data': []},
        'songs':
            {'headers': ('song_title', 'artist_name', 'album_title',
                         'lyrics_url', 'lyrics', 'year',),
             'data': []}}
    """The scraped data is saved as a dictionary.

    .. _scraped-data-Label:

    Its keys and values are defined as follow:

        .. code:: python

            scraped_data = {
                'albums': {
                    'headers': ('album_title', 'artist_name', 'year',),
                    'data': []
                },
                'artists': {
                    'headers': ('artist_name',),
                    'data': []
                },
                'songs': {
                    'headers': ('song_title', 'artist_name', 'album_title',
                                'lyrics_url', 'lyrics', 'year',),
                    'data': []
                }
            }

    .. note:: The 'data' key points to a list of tuple that eventually will 
       store the scraped data from different URLs, i.e. each scraped data from  
       a given URL is added as a tuple to the list.
    """
    # TODO: add example of data.

    def __init__(self, lyrics_urls, db_filepath="", autocommit=False,
                 overwrite_db=False, update_tables=False, cache_dirpath="",
                 overwrite_webpages=False, http_get_timeout=5,
                 delay_between_requests=8, headers=SaveWebpages.headers,
                 use_logging=False, **kwargs):
        self.lyrics_urls = lyrics_urls
        self.skipped_urls = {}
        self.good_urls = set()
        self.checked_urls = set()
        # =============
        # Logging setup
        # =============
        self.use_logging = use_logging
        self.logger_p = logging.getLogger(__name__)
        # Experimental option: add color to log messages
        if os.environ.get('COLOR_LOGS'):
            from pyutils.log.logging_wrapper import LoggingWrapper
            self.logger_p = LoggingWrapper(self.logger_p,
                                           os.environ.get('COLOR_LOGS'))
        if self.use_logging:
            # Before setting up logging from a logging config file, make sure
            # that logging was not already setup previously by a script
            # Get the all the logger's handlers
            handlers = self.logger_p.handlers
            # If there is only one handler and this handler is the NullHandler,
            # then the logger can be setup with the logging config file
            if len(self.logger_p.handlers) == 1 and \
                    isinstance(handlers[0], NullHandler):
                # Setup logging for all custom modules based on the default
                # YAML logging config file
                setup_logging(self.logging_filepath)
                self.logger_p.info("Logging is setup")
            else:
                self.logger_p.warning("The logger was already setup for "
                                      "{}".format(__name__))
        # ===================================
        # Database and scraped data variables
        # ===================================
        if db_filepath is None:
            # No database used
            db_filepath = ""
        self.db_filepath = os.path.expanduser(db_filepath)
        self.autocommit = autocommit
        self.overwrite_db = overwrite_db
        self.update_tables = update_tables
        if self.db_filepath:
            # Create music db
            create_db(self.overwrite_db, self.db_filepath, self.schema_filepath)
            # Connect to the music database
            self.db_conn = self._connect_db()
        else:
            # No database to be used
            self.db_conn = None
        # ===============
        # Cache variables
        # ===============
        if cache_dirpath is None:
            # No cache used. Thus, the webpages will not be saved on disk.
            cache_dirpath = ""
        self.cache_dirpath = os.path.expanduser(cache_dirpath)
        self.overwrite_webpages = overwrite_webpages
        # ======================
        # HTTP request variables
        # ======================
        self.http_get_timeout = http_get_timeout
        self.delay_between_requests = delay_between_requests
        self.headers = headers
        # Create instance for retrieving and saving webpages
        self.saver = SaveWebpages(
            overwrite_webpages=self.overwrite_webpages,
            http_get_timeout=self.http_get_timeout,
            delay_between_requests=self.delay_between_requests,
            headers=self.headers)

    def start_scraping(self):
        """Start the web scraping of lyrics websites.

        This method iterates through each lyrics URL from the main config file
        and delegates the important tasks (URL processing and scraping) to
        separate methods (`_process_url()` and `_scrape_webpage()`).

        Notes
        -----
        This method catches all exceptions that prevent a given URL of being
        processed further, e.g. the webpage is not found (404 Error) or the URL
        is not from a valid domain.

        Any exception that is not caught here is redirected to the main script
        calling this method. See for example the main script
        :mod:`scripts.scraper`.

        """
        # Process list of URLs to lyrics websites
        for url in self.lyrics_urls:
            skip_url = True
            error = None
            try:
                webpage_filename = self._process_url(url)
                self._scrape_webpage(url, webpage_filename)
            except OSError as e:
                self.logger_p.exception(e)
                error = e
            except urllib.error.URLError as e:
                self.logger_p.exception(e)
                self.logger_p.warning(
                    "The URL {} seems to be down!".format(url))
                error = e
            except (connec_exc.HTTP404Error,
                    files_exc.OverwriteFileError,
                    scraper_exc.CurrentSessionURLError,
                    scraper_exc.InvalidURLDomainError,
                    scraper_exc.InvalidURLCategoryError,
                    scraper_exc.MultipleLyricsURLError,
                    scraper_exc.OverwriteSongError,
                    sql_exc.SQLSanityCheckError) as e:
                self.logger_p.error(e)
                error = e
            else:
                skip_url = False
            finally:
                # Close db connection
                self.db_conn.close()
                # Add the URL as skipped or good
                if skip_url:
                    self._add_skipped_url(url, get_error_msg(error))
                else:
                    self.logger_p.debug("URL successfully processed:"
                                        " {}".format(url))
                    self.good_urls.add(url)

    def get_scraped_data(self):
        """Return the scraped data as a dictionary.

        This method returns all the data that was scraped from the lyrics
        webpages. If a database was used, the scraped data is also saved in the
        SQLite database file found at :ref:`db_filepath
        <LyricsScraperParametersLabel>`

        See :ref:`scraped_data <scraped-data-Label>` for a detailed structure of
        the returned dictionary.

        Returns
        -------
        scraped_data : dict
            The scraped data whose content is described in
            :data:`~scrapers.lyrics_scraper.LyricsScraper.scraped_data`.

        """
        # If a db was used, inform the user that the scraped data is also to be
        # found in the SQLite database that was initially configured.
        if self.db_conn:
            self.logger_p.info("The scraped data is also saved in the database"
                               " '{}'".format(self.db_filepath))
        return self.scraped_data

    def _add_skipped_url(self, url, error):
        """Add an URL as skipped.

        The skipped URL is added to a dictionary along with its error message
        which explains why it was skipped.

        Parameters
        ----------
        url : str
            The skipped URL which will be added to the dictionary along with its
            corresponding error message.
        exc : Exception
            The error message as an :exc:`Exception`, e.g. :exc:`TypeError`, which
            will be converted to a string and added to the dictionary along with
            its corresponding URL.

        """
        self.logger_p.warning("Skipping the URL {}".format(url))
        self.skipped_urls.setdefault(url, [])
        self.skipped_urls[url].append(str(error))

    def _check_url_if_processed(self, url):
        """Check if an URL was already processed.

        First, the URL is checked if it was already processed during the current
        session.

        Then, the URL is checked if is already present in the database (if a
        database was used of course).

        By doing these checks, we reduce a lot of computations that would have
        been unnecessary, like scraping and saving an already processed webpage.

        Parameters
        ----------
        url : str
            The URL to be checked if it was previously processed.

        Raises
        ------
        CurrentSessionURLError
            Raised if the URL was already processed during this session.

        """
        # First, check if URL already processed during current session
        if url in self.checked_urls:
            raise scraper_exc.CurrentSessionURLError(
                "The url {} was already processed during this"
                " session".format(url))
        elif self.db_conn:
            # Check if URL in db
            self._check_url_in_db(url)
        else:
            # URL is brand new! Thus, it can be further processed.
            self.logger_p.debug("The url {} was not previously"
                                " processed".format(url))
            self.checked_urls.add(url)

    def _check_url_in_db(self, url):
        """Check if an URL is already present in the database.

        The first thing to do when processing a given artist or lyrics URL is
        to check if it has not already been processed previously, i.e. verify
        if the URL is already in the db. Hence, we speed up the program
        execution.

        Parameters
        ----------
        url : str
            URL to be checked if it is already in the db.

        Raises
        ------
        MultipleLyricsURLError
            Raised if an URL was found more than once in the music db.
        OverwriteSongError
            Raised if a song was already found in the db and the db can't be
            updated because the :ref:`update_tables
            <LyricsScraperParametersLabel>` flag is disabled.

        """
        # Select all songs with the given URL from the music db
        res = self._select_song(url)
        if len(res) == 1:
            # Only one song found with the given URL
            self.logger_p.debug("There is already a song with the same URL"
                                " {}".format(url))
            # Check if the song found with the given URL can be updated
            # (overwritten) in the table
            if self.update_tables:
                # Song can be updated
                self.logger_p.debug("Since the 'update_tables' flag is set to"
                                    " True, the URL will be processed and the"
                                    " music db will be updated as a consequence")
            else:
                # Song can't be updated
                raise scraper_exc.OverwriteSongError(
                    "Since the 'update_tables' flag is set to False, the URL"
                    " will be ignored")
        elif len(res) == 0:
            # No song found with the given URL
            self.logger_p.debug("The lyrics URL {} was not found in the music"
                                " db".format(url))
        else:
            # Odd case: more than one song was found with the given URL
            raise scraper_exc.MultipleLyricsURLError(
                "The lyrics URL {} was found more than once in the music"
                " db".format(url))

    def _connect_db(self):
        """Connect to the SQLite music database.

        The SQLite music database is used for saving any relevant data from the
        scraped webpages.

        See the structure of the music database as defined in the `music.sql
        schema`_.

        Returns
        -------
        conn : sqlite3.Connection
            Connection object that represents the SQLite database.

        Raises
        ------
        sqlite3.Error
             Raised if any SQLite-related error occurs, such as
             :exc:`sqlite3.IntegrityError` or :exc:`sqlite3.OperationalError`.

        """
        # Connect to the music database
        try:
            self.logger_p.info("Connecting to db '{}'".format(self.db_filepath))
            conn = connect_db(self.db_filepath, self.autocommit)
        except sqlite3.Error as e:
            raise sqlite3.Error(e)
        else:
            self.logger_p.debug("Db connection established!")
            return conn

    def _count_empty_items(self, data):
        """Count empty items in a tuple.

         Returns the number of empty items in a list or tuple which can be empty
         strings or :obj:`None`.

        Parameters
        ----------
        data : list or tuple
            The tuple whose content will be checked for number of empty items.

        Returns
        -------
        count : int
            The number of empty items (empty strings or :obj:`None`) in the tuple.

        Notes
        -----
        A warning that empty items are found is logged.

        """
        # Count number of empty items in the list/tuple
        count = sum([1 for f in data if not f])
        if count:
            # At least one empty item found
            self.logger_p.warning("Empty field{}: {}".format(
                add_plural_ending(count), data))
        return count

    def _get_html(self, webpage_filepath, url):
        """Get the HTML content for a given URL and save its content if possible.

        The webpage HTML is retrieved for a given URL and if the cache is used,
        its HTML content is saved.

        Parameters
        ----------
        webpage_filepath : str
            The path to the webpage saved on disk if cache is used.
        url : str
            The URL

        Returns
        -------
        html : str
            The HTML content of the webpage.

        """
        # Save the webpage and retrieve its html content
        if self.cache_dirpath:
            # Cache the webpage
            html = self.saver.save_webpage(webpage_filepath, url)
        else:
            # Don't cache the webpage, just retrieve its html content
            html = self.saver.get_webpage(url)
        return html

    def _process_url(self, url):
        """Process each URL defined in the YAML config file.

        The URLs can refer to an artist or lyrics webpage. In order to reduce
        the number of HTTP requests to the lyrics website, the URL is first
        checked if it has already been processed.

        Parameters
        ----------
        url : str
            URL to the artist's or lyrics webpage that will be scraped.

        Returns
        -------
        webpage_filepath : str
            File path where the webpage's HTML will be cached.

        Raises
        ------
        InvalidURLDomainError
            Raised if the URL is not from a valid domain. See
            :data:`~LyricsScraper.valid_domains`.

        Notes
        -----
        There is a more robust parsing of the top-level domain: `use a
        specialized library`_ (e.g. tldextract). For example, `urlparse`
        will not be able to extract the right domain from a more complex URL
        such as 'http://forums.news.cnn.com/'. On the other hand, `tldextract`
        will output 'cnn' which is correct.

        """
        self.logger_p.info("Processing the URL {}".format(url))
        # Check first if the URL was already processed, e.g. is found in the db
        self._check_url_if_processed(url)
        domain = urlparse(url).netloc

        # Get the name of the directory in cache where the webpages are/will be
        # saved
        if self.cache_dirpath:
            # Cache to be used. Webpages will be saved on disk.
            webpages_dirpath = os.path.join(self.cache_dirpath, domain)
            webpage_filepath = os.path.join(webpages_dirpath,
                                            os.path.basename(url))
        else:
            # No cache used. Thus, the webpages will not be saved on disk.
            webpages_dirpath = ""
            webpage_filepath = ""

        # Check if the webpage associated with the URL is already cached
        if os.path.isfile(webpage_filepath):
            # NOTE: if None is given to os.path.isfile(), it complains with this
            # error:
            # TypeError: stat: path should be string, bytes, os.PathLike or integer,
            # not NoneType
            self.logger_p.info("The webpage {} was found in cache @ '{}'".format(
                url, webpage_filepath))
        else:
            # The given webpage is brand new!
            self.logger_p.info("We will retrieve the webpage {}".format(url))
            # Check if the URL is available
            # NOTE: it can also be done with requests which is not
            # installed by default on Python.
            self.logger_p.debug("Checking if the URL {} is"
                                " available".format(url))
            code = urlopen(url).getcode()
            self.logger_p.debug("The URL {} is up. Status code:"
                                " {}".format(url, code))
            self.logger_p.debug("Validating the URL's domain")

            # Validate URL's domain
            if domain in self.valid_domains:
                self.logger_p.debug("The domain '{}' is valid".format(domain))
            else:
                raise scraper_exc.InvalidURLDomainError(
                    "The URL's domain '{}' is invalid. Only URLs from"
                    " {} are accepted.".format(domain, self.valid_domains))

            # Create directory for caching the webpage
            if self.cache_dirpath:
                try:
                    create_directory(webpages_dirpath)
                except FileExistsError as e:
                    self.logger_p.warning(e)

        return webpage_filepath

    def _scrape_webpage(self, url, webpage_filepath):
        """Scrape a given webpage and save the scraped data.

        It crawls the webpage and scrapes any useful info to be saved, such as
        the song's title and the lyrics text.

        The scraped data is saved in the :data:`~LyricsScraper.scraped_data`
        dictionary and in a database (if it was initially configured).

        If the cache is used, the webpage HTML is also save on disk to reduce
        the number of requests to the server.

        Parameters
        ----------
        url: str
            The URL of the webpage to be scraped.
        webpage_filepath : str
            The path of the webpage where its HTML will be saved if the cache
            is used.

        """
        raise NotImplementedError("The _scrape_webpage() method needs to be"
                                  " implemented by the derived classes of"
                                  " LyricsScraper.")

    def _save_album(self, album_title, artist_name, year):
        """Save the scraped data about an album.

        The data will be saved in the `scraped_data` dictionary and a database
        if it was initially configured.

        Parameters
        ----------
        album_title : str
            The title of the album.
        artist_name : str
            The name of the artist.
        year : str
            The year the album was published.

        Notes
        -----
        If the album title and artist name are missing (i.e. empty strings), the
        album data will not be saved.

        """
        album_tuple = (album_title, artist_name, year,)
        self.logger_p.debug("Saving the album {}".format(album_tuple))
        # Save album only if album and artist name are not missing
        if not self._count_empty_items(album_tuple[0:2]):
            if self.db_conn:
                # Save data into db
                self._insert_album(album_tuple)
            # Save data into dict
            self._update_scraped_data(
                album_tuple, self.scraped_data['albums']['data'])
        else:
            self.logger_p.warning("Album couldn't be saved!")

    def _save_artist(self, artist_name):
        """Save the scraped data about an artist.

        The data will be saved in the :data:`~LyricsScraper.scraped_data`
        dictionary and a database if it was initially configured.

        Parameters
        ----------
        artist_name : str
            The name of the artist.

        Notes
        -----
        If the artist name is missing (i.e. empty string), the artist data will
        not be saved.

        """
        artist_tuple = (artist_name,)
        self.logger_p.debug("Saving the artist {}".format(artist_tuple))
        # Save album only if artist name is not missing
        if not self._count_empty_items(artist_tuple):
            if self.db_conn:
                # Save data into db
                self._insert_artist(artist_tuple)
            # Save data into dict
            self._update_scraped_data(
                artist_tuple, self.scraped_data['artists']['data'])
        else:
            self.logger_p.warning("Artist couldn't be saved!")

    def _save_song(self, song_title, artist_name, album_title, lyrics_url,
                   lyrics, year):
        """Save the scraped data about a song.

        The data will be saved in the :data:`~LyricsScraper.scraped_data`
        dictionary and a database if it was initially configured.

        Parameters
        ----------
        song_title : str
            The title of the song
        artist_name : str
            The name of the artist.
        album_title : str
            The title of the album.
        lyrics_url : str
            The URL to the lyrics webpage where the scraped data comes from.
        lyrics : str
            The text lyrics.
        year : str
            The year the song was published.

        Notes
        -----
        If the song title is missing (i.e. empty string), the song data will
        not be saved.

        """
        song_tuple = (song_title, artist_name, album_title, lyrics_url, lyrics,
                      year)
        self.logger_p.debug("Saving the song {}".format(song_tuple))
        # Save album only if the song title is not missing
        if not self._count_empty_items(song_tuple[0:1]):
            if self.db_conn:
                # Save data into db
                self._insert_song(song_tuple)
            # Save data into dict
            self._update_scraped_data(
                song_tuple, self.scraped_data['songs']['data'])
        else:
            self.logger_p.warning("Song couldn't be saved!")

    def _update_scraped_data(self, data_tuple, scraped_data):
        """Update scraped data.

        Update the list of scraped by adding the tuple of data.

        The tuple of data must be **unique** in order to be added to the list
        of scraped data.

        Parameters
        ----------
        data_tuple : tuple
            The tuple of data to be added to the list of scraped data.
        scraped_data : list
            The list of scraped data where the tuple of data will be added.

        """
        # Check if tuple of data is unique
        if data_tuple in scraped_data:
            # Tuple of data is not unique
            self.logger_p.debug("Scraped data already previously saved:"
                                " {}".format(data_tuple))
        else:
            # Tuple of data is unique. Thus, save it.
            scraped_data.append(data_tuple)
            self.logger_p.debug("Scraped data successfully saved:"
                                " {}".format(data_tuple))

    def _execute_sql(self, sql, values):
        """Execute an SQL expression.

        The SQL expression can be a SELECT or an INSERT query.

        If it is a SELECT query, a list of tuple is returned. If it is an
        INSERT query, then the id of the last row in the updated table is
        returned.

        Parameters
        ----------
        sql : str
            SQL query to be executed.
        values : tuple of str
            The values associated with the query (e.g. the values to be
            inserted if it is an INSERT query).

        Returns
        -------
        cur.fetchall() : list of tuple
            List of tuple from the executed SELECT query, where each tuple
            represents one row entry.

            .. important::

               This returned value only happens with SELECT queries.
        None
            Returned if the table couldn't be updated because of an
            :exc:`sqlite3.IntegrityError` exception.

            .. important::

               This returned value only happens with INSERT queries.

            It is not a fatal exception that should stop the program execution
            since the exception can occur when the data to be inserted is
            already in the database which is a common case (e.g. if we add
            songs from the same artist, the artist name wilL only be added
            once). If this case happens, we add the rest of the scraped data.
        lastrowid : int
            The id of the last row in the updated table, after the insertion
            was successful.

            .. important::

               This returned value only happens with INSERT queries.

        Raises
        ------
        SQLSanityCheckError
            Raised if a sanity check on the SQL query failed, e.g. the
            query's values are not of :obj:`tuple` type or wrong number of
            values in the SQL query.

        Notes
        -----
        `values` is needed only in the case of an INSERT query since we are
        inserting data into the db, unlike a SELECT query which only retrieve
        data from the db.

        When executing an INSERT query, the returned value (i.e. `lastrowid`)
        is not used within the corresponding INSERT method, e.g.
        :meth:`~LyricsScraper._insert_album`.

        Check this `guide`_ for more information about SQLite database
        operations.

        .. important::

           See the structure of the music database as defined in the `music.sql
           schema`_.

        """
        cur = self.db_conn.cursor()
        try:
            sql_sanity_check(sql, values)
            cur.execute(sql, values)
        except sqlite3.IntegrityError as e:
            # Duplicate data can't be inserted
            self.logger_p.debug(e)
            return None
        except sql_exc.SQLSanityCheckError as e:
            # One of the SQL sanity checks failed
            self.logger_p.error(e)
            raise sql_exc.SQLSanityCheckError(e)
        else:
            # Successful SQL expression execution
            if sql.lower().startswith("select"):
                # SELECT query
                return cur.fetchall()
            else:
                # INSERT query
                if not self.autocommit:
                    # Since autocommit is disabled, we must manually commit
                    # all pending changes to the database
                    self.db_conn.commit()
                self.logger_p.debug("Query execution successful!"
                                    " lastrowid={}".format(cur.lastrowid))
                return cur.lastrowid

    def _insert_album(self, album):
        """Insert data about an album in the database.

        Data about an album can consist in the album' title and the year the
        album was published.

        See the `albums` table as defined in the `music.sql schema`_.

        Parameters
        ----------
        album : tuple of str
            The tuple contains the relevant data about an album that will be
            added to the database, such as the album title, the artist name, and
            the year the album was published.

        """
        sql = "INSERT INTO albums (album_title, artist_name, year)" \
              " VALUES (?, ?, ?)"
        self._execute_sql(sql, album)

    def _insert_artist(self, artist_name):
        """Insert an artist's name in the database.

        An artist's name can refer to a group or an individual (solo).

        See the `artists` table as defined in the `music.sql schema`_.

        Parameters
        ----------
        artist_name : tuple of str
            The tuple contains the name of the artist that will be added to the
            database.

        """
        sql = "INSERT INTO artists (artist_name) VALUES (?)"
        self._execute_sql(sql, artist_name)

    def _insert_song(self, song):
        """Insert data about a song in the database.

        The data about a song that will be added to the database can consist to
        the song title, artist name, and album title.

        See the `songs` table as defined in the `music.sql schema`_.

        Parameters
        ----------
        song : tuple of str
            The tuple contains the relevant data about a song that will be
            added to the database, such as the song title, the artist name, and
            the lyrics text.

        """
        sql = "INSERT INTO songs (song_title, artist_name, album_title," \
              " lyrics_url, lyrics, year) VALUES (?, ?, ?, ?, ?, ?)"
        self._execute_sql(sql, song)

    def _select_song(self, lyrics_url):
        """Select a song from the database based on a lyrics URL.

        The lyrics URL is used as the WHERE condition to be used for retrieving
        the associated song from the database.

        See the `songs` table as defined in the `music.sql schema`_.

        Parameters
        ----------
        lyrics_url : str
            Lyrics URL to be used in the WHERE condition of the SELECT query.

        Returns
        -------
        cur.fetchall() : list of tuple
            List of tuple from the executed SELECT query, where each tuple
            represents one row entry.

        """
        self.logger_p.debug("Selecting the song where"
                            " lyrics_url={}".format(lyrics_url))
        sql = "SELECT * FROM songs WHERE lyrics_url=?"
        return self._execute_sql(sql, (lyrics_url,))
