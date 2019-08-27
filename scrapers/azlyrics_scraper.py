import os
import re
from urllib.request import urlopen
from urllib.parse import urlparse
# Third-party modules
import ipdb
from bs4 import BeautifulSoup
# Own modules
import scrapers.exc as music_exc
from scrapers.lyrics_scraper import LyricsScraper
import utilities.exc as utils_exc
from utilities.genutils import add_plural, create_directory
from utilities.logging_boilerplate import LoggingBoilerplate
from utilities.logging_wrapper import LoggingWrapper


# Scrapes and saves webpages locally
class AZLyricsScraper(LyricsScraper):
    VALID_DOMAIN = "www.azlyrics.com"

    def __init__(self, main_cfg, logger):
        super().__init__(main_cfg, logger)
        if isinstance(logger, dict):
            lb = LoggingBoilerplate(__name__,
                                    __file__,
                                    os.getcwd(),
                                    logger)
            self.logger = lb.get_logger()
        else:
            # Sanity check on `logger`
            assert isinstance(logger, LoggingWrapper), \
                "`logger` must be of type `LoggingWrapper`"
            self.logger = logger

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
