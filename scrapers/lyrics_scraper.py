import os
import sqlite3
# NOTE 1: I'm using `requests` in ../save_webpages/run_saver.py
# NOTE 2: For urllib with Python 2, it is
# `from six.moves.urllib.parse import urlparse`
import urllib
# Third-party modules
import ipdb
# Own modules
import scrapers.exc as music_exc
from utilities.genutils import connect_db
from utilities.logging_boilerplate import LoggingBoilerplate
from utilities.logging_wrapper import LoggingWrapper
from utilities.save_webpages import SaveWebpages


# Scrapes and saves webpages locally
class LyricsScraper:
    def __init__(self, main_cfg, logger=None):
        self.main_cfg = main_cfg
        if isinstance(logger, dict):
            lb = LoggingBoilerplate(__name__,
                                    __file__,
                                    os.getcwd(),
                                    logger)
            self.logger_p = lb.get_logger()
        else:
            # Sanity check on `logger`
            assert isinstance(logger, LoggingWrapper), \
                "`logger` must be of type `LoggingWrapper`"
            self.logger_p = logger
        self.music_db_filepath = \
            os.path.expanduser(main_cfg['music_db_filepath'])
        self.cache_webpages = os.path.expanduser(main_cfg['cache_webpages'])
        self.lyrics_urls = main_cfg['lyrics_urls']
        self.music_conn = None
        self.saver = SaveWebpages(main_cfg=self.main_cfg,
                                  logger=logger)

    def start_scraping(self):
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
            except (music_exc.InvalidURLDomainError,
                    music_exc.InvalidURLCategoryError) as e:
                self.logger_p.error(e)
                self.logger_p.info("Skipping the URL {}".format(url))
            except (music_exc.MultipleLyricsURLError,
                    music_exc.OverwriteSongError) as e:
                self.logger_p.info(e)
                self.logger_p.info("Skipping the URL {}".format(url))

    def _connect_db(self):
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
        # Check first if the URL was already processed, i.e. is found in the db
        res = self._select_song(url)
        if len(res) == 1:
            self.logger_p.debug(
                "There is already a song with the same URL {}".format(url))
            if self.main_cfg['overwrite_db']:
                self.logger_p.debug(
                    "Since the 'overwrite_db' flag is set to True, the URL "
                    "will be processed and the music db will be updated as a "
                    "consequence")
            else:
                raise music_exc.OverwriteSongError(
                    "Since the 'overwrite_db' flag is set to False, the URL "
                    "will be ignored")
        elif len(res) == 0:
            self.logger_p.debug(
                "The lyrics URL {} was not found in the music db".format(url))
        else:
            raise music_exc.MultipleLyricsURLError(
                "The lyrics URL {} was found more than once in the music "
                "db".format(url))

    def _crawl_artist_page(self, artist_filename, artist_url):
        raise NotImplementedError

    def _crawl_lyrics_page(self, lyrics_filename, lyrics_url):
        raise NotImplementedError

    def _process_url(self, url):
        raise NotImplementedError

    def _execute_sql(self, cur, sql, values):
        self.sanity_check_sql(sql, values)
        try:
            cur.execute(sql, values)
        except sqlite3.IntegrityError as e:
            self.logger_p.debug(e)
            return None
        else:
            if not self.main_cfg['autocommit']:
                self.music_conn.commit()
            self.logger_p.debug(
                "Query execution successful! lastrowid={}".format(cur.lastrowid))
            return cur.lastrowid

    def _insert_album(self, album):
        self.logger_p.debug(
            "Inserting the album: album_title={}, artist_name={}, "
            "year={}".format(album[0], album[1], album[2]))
        sql = "INSERT INTO albums (album_title, artist_name, year) " \
              "VALUES (?, ?, ?)"
        cur = self.music_conn.cursor()
        self._execute_sql(cur, sql, album)

    def _insert_artist(self, artist_name):
        self.logger_p.debug("Inserting the artist: {}".format(artist_name[0]))
        sql = '''INSERT INTO artists (artist_name) VALUES (?)'''
        cur = self.music_conn.cursor()
        self._execute_sql(cur, sql, artist_name)

    def _insert_song(self, song):
        self.logger_p.debug(
            "Inserting the song: song_title={}, artist_name={}, "
            "album_title={}".format(song[0], song[1], song[4]))
        sql = "INSERT INTO songs (song_title, artist_name, lyrics, " \
              "lyrics_url, album_title, year) VALUES (?, ?, ?, ?, ?, ?)"
        cur = self.music_conn.cursor()
        self._execute_sql(cur, sql, song)

    def _select_song(self, lyrics_url):
        self.logger_p.debug(
            "Selecting the song where lyrics_url={}".format(lyrics_url))
        sql = "SELECT * FROM songs WHERE lyrics_url='{}'".format(
            lyrics_url)
        cur = self.music_conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    @staticmethod
    def sanity_check_sql(sql, val):
        assert type(val) is tuple, \
            "The values for the SQL expression are not of `tuple` type"
        assert len(val) == sql.count('?'), \
            "Wrong number of values ({}) in the SQL expression '{}'".format(
                len(val), sql)
