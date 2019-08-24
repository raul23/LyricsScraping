import os
import re
import sqlite3
# NOTE 1: I'm using `requests` in ../save_webpages/run_saver.py
# NOTE 2: For urllib with Python 2, it is
# `from six.moves.urllib.parse import urlparse`
import urllib
from urllib.request import urlopen
from urllib.parse import urlparse
# Third-party modules
import ipdb
from bs4 import BeautifulSoup
# Own modules
import scrapers.exc as music_exc
import utilities.exc as utils_exc
from utilities.genutils import add_plural, connect_db, create_directory
from utilities.save_webpages import SaveWebpages


# Scrapes and saves webpages locally
class LyricsScraper:
    VALID_DOMAIN = "www.azlyrics.com"

    def __init__(self, main_cfg, logging_cfg, logger):
        self.main_cfg = main_cfg
        self.logging_cfg = logging_cfg
        self.logger = logger
        self.music_db_filepath = \
            os.path.expanduser(main_cfg['music_db_filepath'])
        self.cache_webpages = os.path.expanduser(main_cfg['cache_webpages'])
        self.lyrics_urls = main_cfg['lyrics_urls']
        self.music_conn = None
        self.saver = SaveWebpages(main_cfg=self.main_cfg,
                                  logger=self.logger)

    def start_scraping(self):
        # Connect to the music database
        try:
            self.logger.info(
                "Connecting to db '{}'".format(self.music_db_filepath))
            self.music_conn = connect_db(self.music_db_filepath)
        except sqlite3.Error as e:
            raise sqlite3.Error(e)
        else:
            self.logger.debug("Db connection established!")
        ipdb.set_trace()
        # Process list of URLs to lyrics websites
        for url in self.lyrics_urls:
            try:
                self._process_url(url)
            except urllib.error.URLError as e:
                self.logger.exception(e)
                self.logger.warning(
                    "The URL {} seems to be down!".format(url))
                self.logger.info("Skipping the URL {}".format(url))
            except (music_exc.InvalidURLDomainError,
                    music_exc.InvalidURLCategoryError) as e:
                self.logger.error(e)
                self.logger.info("Skipping the URL {}".format(url))
            except (music_exc.MultipleLyricsURLError,
                    music_exc.OverwriteSongError) as e:
                self.logger.info(e)
                self.logger.info("Skipping the URL {}".format(url))

    def _check_url_in_db(self, url):
        # Check first if the URL was already processed, i.e. is found in the db
        res = self._select_song(url)
        if len(res) == 1:
            self.logger.debug(
                "There is already a song with the same URL {}".format(url))
            if self.main_cfg['overwrite_db']:
                self.logger.debug(
                    "Since the 'overwrite_db' flag is set to True, the URL {} "
                    "will be processed and the music db will be updated as a "
                    "consequence.".format(url))
            else:
                raise music_exc.OverwriteSongError(
                    "Since the 'overwrite_db' flag is set to False, the URL {} "
                    "will be ignored.".format(url))
        elif len(res) == 0:
            self.logger.debug(
                "The lyrics URL {} was not found in the music db".format(url))
        else:
            raise music_exc.MultipleLyricsURLError(
                "The lyrics URL {} was found more than once in the music "
                "db".format(url))

    def _crawl_artist_page(self, artist_filename, artist_url):
        self.logger.debug(
            "Crawling the artist webpage {}".format(artist_url))
        # Load the webpage or save the webpage and retrieve its html
        html = None
        try:
            html, webpage_accessed = \
                self.saver.save_webpage(artist_filename, artist_url, False)
        except utils_exc.WebPageNotFoundError as e:
            self.logger.exception(e)
        bs_obj = BeautifulSoup(html, 'lxml')
        # Get the name of the artist
        artist_name = bs_obj.title.text.split(' Lyrics')[0]
        # Insert artist to database
        self._insert_artist((artist_name, ))
        # Get the list of lyrics' URLs from the given artist
        anchors = bs_obj.find_all("a", href=re.compile("^../lyrics"))
        # Process each lyrics' url
        self.logger.info("There are {} lyrics URLs to process for the given "
                         "artist".format(len(anchors)))
        for i, a in enumerate(anchors):
            lyrics_url = a.attrs['href']
            self.logger.info(
                "#{} Processing the lyrics URL {}".format(i+1, lyrics_url))
            self.logger.debug("Processing the anchor '{}'".format(a))
            # Check if the lyrics' URL is relative to the current artist's URL
            # NOTE: this only happens with www.azlyrics.com
            self.logger.debug(
                "Checking if the URL {} is relative".format(lyrics_url))
            if lyrics_url.startswith('../'):
                self.logger.debug(
                    "The URL {} is relative".format(lyrics_url))
                parsed_url = urlparse(artist_url)
                lyrics_url = '{}://{}{}'.format(parsed_url.scheme,
                                                parsed_url.hostname,
                                                lyrics_url[2:])
            # Build the filename where the lyrics webpage will be saved
            lyrics_filename = os.path.join(os.path.dirname(artist_filename),
                                           os.path.basename(lyrics_url))
            self._crawl_lyrics_page(lyrics_filename, lyrics_url)

    def _crawl_lyrics_page(self, lyrics_filename, lyrics_url):
        try:
            # Check first if the URL was already processed, i.e. is found in
            # the db
            self._check_url_in_db(lyrics_url)
            self.logger.debug(
                "Crawling the lyrics webpage {}".format(lyrics_url))
            # Load the webpage or save the webpage and retrieve its html
            html = None
            try:
                html, webpage_accessed = \
                    self.saver.save_webpage(lyrics_filename, lyrics_url, False)
            except utils_exc.WebPageNotFoundError as e:
                self.logger.exception(e)
                raise utils_exc.WebPageNotFoundError(e)
            bs_obj = BeautifulSoup(html, 'lxml')
            # Get the following data from the lyrics webpage:
            # - the title of the song
            # - the name of the artist
            # - the text of the song
            # - the album title the song comes from
            # - the year the song was published
            song_title = bs_obj.title.text.split('- ')[1].split(' Lyrics')[0]
            artist_name = bs_obj.title.text.split(' -')[0]
            lyrics_res = bs_obj.find_all('div', class_="", id="")
            # Sanity check on lyrics: lyrics are ONLY found within a <div> without
            # class and id
            if len(lyrics_res) > 1:
                raise music_exc.NonUniqueLyricsError(
                    "Lyrics extraction scheme broke: no lyrics found or more than "
                    "one lyrics were found")
            lyrics_text = lyrics_res[0].text.strip()
            album_res = bs_obj.find_all("div",
                                        class_="panel songlist-panel noprint")
            if len(album_res) == 0:
                self.logger.debug(
                    "No album found in the lyrics webpage {}".format(lyrics_url))
                album_title = ""
                song_year = ""
                # Insert the relevant song's data into the db
                self._insert_artist((artist_name,))
                self._insert_song((song_title, artist_name, lyrics_text, lyrics_url,
                                   album_title, song_year))
            else:
                self.logger.debug("{} album{} found".format(
                    len(album_res), add_plural(len(album_res))))
                for album in album_res:
                    album_title = album.contents[1].text.strip('"')
                    year_res = re.findall(r'\d+', album.contents[2])
                    # Sanity checks on the album's year
                    if len(year_res) != 1:
                        raise music_exc.NonUniqueAlbumYearError(
                            "Album's year extraction doesn't result in a UNIQUE "
                            "number")
                    # Only works for songs published in the 20th and 21th centuries
                    if not (year_res[0].startswith('19') or
                            year_res[0].startswith('20')):
                        raise music_exc.WrongAlbumYearError(
                            "Album's year is in the wrong century: only songs "
                            "published in the 20th and 21th centuries are "
                            "supported")
                    song_year = year_res[0]
                    # Insert the relevant song's data into the db
                    self._insert_artist((artist_name, ))
                    self._insert_song((song_title, artist_name, lyrics_text,
                                       lyrics_url, album_title, song_year))
                    # Insert the relevant album's data into the db
                    self._insert_album((album_title, artist_name, song_year))
        except (utils_exc.WebPageNotFoundError,
                music_exc.MultipleAlbumError,
                music_exc.NonUniqueLyricsError,
                music_exc.NonUniqueAlbumYearError,
                music_exc.WrongAlbumYearError) as e:
            self.logger.exception(e)
            self.logger.warning(
                "Skipping the lyrics URL {}".format(lyrics_url))
        except (music_exc.MultipleLyricsURLError,
                music_exc.OverwriteSongError) as e:
            self.logger.info(e)
            self.logger.warning(
                "Skipping the lyrics URL {}".format(lyrics_url))

    def _process_url(self, url):
        self.logger.info("Processing the URL {}".format(url))
        # Check first if the URL was already processed, i.e. is found in the db
        self._check_url_in_db(url)
        domain = urlparse(url).netloc
        # Create the name of the folder where the webpage will be saved
        dir_path = os.path.join(self.cache_webpages, domain)
        webpage_filename = os.path.join(dir_path, os.path.basename(url))

        # Check if the webpage associated with the URL is already cached
        if os.path.isfile(webpage_filename):
            self.logger.info(
                "The webpage {} was found in cache @ '{}'".format(
                    url, webpage_filename))
        else:
            self.logger.warning(
                "The webpage {} was not found in cache".format(
                    webpage_filename))
            self.logger.info(
                "Thus, we will try to retrieve the webpage {}".format
                (url))
            # Check if the URL is available
            # NOTE: it can also be done with `requests` which is not
            # installed by default on Python.
            # References:
            # -
            # -
            # -
            self.logger.debug(
                "Checking if the URL {} is available".format(url))
            code = urlopen(url).getcode()
            self.logger.debug(
                "The URL {} is up. Status code: {}".format(url, code))
            self.logger.debug("Validating the URL's domain")

            # Validate URL's domain
            # There is a more robust parsing of the TLD, use a specialized
            # library (e.g. `tldextract`). For example, `urlparse` will
            # not be able to extract the right domain from a more complex
            # URL such as 'http://forums.news.cnn.com/'. On the other hand,
            # `tldextract` will ouput 'cnn' which is correct.
            # References:
            # - https://stackoverflow.com/a/44022572 : tldextract is more
            #   efficient version of `urlparse`
            # - https://stackoverflow.com/a/44021937 : use `urlparse` but
            #   it might have some problems with some URLs
            # - https://stackoverflow.com/a/44113853 : use `urlparse` and
            #   how to get the domain without the subdomain
            # - https://stackoverflow.com/a/45022556 : `tldextract` also
            #   works with emails and you install it with
            #   `pip install tldextract`
            # - https://stackoverflow.com/a/51726087 : use
            #   `os.path.basename` if you want to extract a filename from
            #   the URL but it has its own problems with URLS having a
            #   query string
            if domain in self.VALID_DOMAIN:
                self.logger.debug(
                    "The domain '{}' is valid".format(domain))
            else:
                raise music_exc.InvalidURLDomainError(
                    "The URL's domain '{}' is invalid. Only URLs from "
                    "www.azlyrics.com are accepted.")

            # Create directory for caching the webpage
            try:
                create_directory(dir_path)
            except ResourceWarning as e:
                self.logger.warning(e)

        # Check if the azlyrics URL belongs to a lyrics or artist
        # and start the crawling of the actual webpage with BeautifulSoup
        if urlparse(url).path.startswith('/lyrics/'):
            self.logger.debug(
                "The URL {} refers to a lyrics' webpage".format(url))
            self._crawl_lyrics_page(webpage_filename, url)
        elif urlparse(url).path.startswith('/19/') or \
                urlparse(url).path[1].isalpha():
            # NOTE: webpages of artists' names that start with a number are
            # placed within the directory /19/
            # e.g. https://www.azlyrics.com/19/50cent.html
            self.logger.debug(
                "The URL {} refers to an artist's webpage".format(url))
            self._crawl_artist_page(webpage_filename, url)
        else:
            raise music_exc.InvalidURLCategoryError(
                "The URL {} is not recognized as referring to neither "
                "an artist's nor a song's webpage ".format(url))

    def _execute_sql(self, cur, sql, values):
        self.sanity_check_sql(sql, values)
        try:
            cur.execute(sql, values)
        except sqlite3.IntegrityError as e:
            self.logger.debug(e)
            return None
        else:
            if not self.main_cfg['autocommit']:
                self.music_conn.commit()
            self.logger.debug(
                "Query execution successful! lastrowid={}".format(cur.lastrowid))
            return cur.lastrowid

    def _insert_album(self, album):
        self.logger.debug(
            "Inserting the album: album_title={}, artist_name={}, "
            "year={}".format(album[0], album[1], album[2]))
        sql = "INSERT INTO albums (album_title, artist_name, year) " \
              "VALUES (?, ?, ?)"
        cur = self.music_conn.cursor()
        self._execute_sql(cur, sql, album)

    def _insert_artist(self, artist_name):
        self.logger.debug("Inserting the artist: {}".format(artist_name[0]))
        sql = '''INSERT INTO artists (artist_name) VALUES (?)'''
        cur = self.music_conn.cursor()
        self._execute_sql(cur, sql, artist_name)

    def _insert_song(self, song):
        self.logger.debug(
            "Inserting the song: song_title={}, artist_name={}, "
            "album_title={}".format(song[0], song[1], song[4]))
        sql = "INSERT INTO songs (song_title, artist_name, lyrics, " \
              "lyrics_url, album_title, year) VALUES (?, ?, ?, ?, ?, ?)"
        cur = self.music_conn.cursor()
        self._execute_sql(cur, sql, song)

    def _select_song(self, lyrics_url):
        self.logger.debug(
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
