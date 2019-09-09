"""Module that defines the derived class for scraping artist and lyrics
webpages from www.azlyrics.com

``AZLyricsScraper`` is derived from the base class ``LyricsScraper``. This
class crawls and scrapes artist and lyrics webpages from www.azlyrics.com
for useful data to be added in the music database, such as the artist's name,
the album's title, and the lyrics text.

In order to reduce the number of HTTP requests to the lyrics website, the
webpages are saved in cache.

See the structure of the music database as defined in the
`music.sql schema
<https://github.com/raul23/lyrics-scraper/blob/master/database/music.sql/>`_.

"""

import os
import re
from urllib.request import urlopen
from urllib.parse import urlparse
# Third-party modules
from bs4 import BeautifulSoup
# Custom modules
import scrapers.scraper_exceptions as music_exc
import utils.exceptions.connection as connec_exc
import utils.exceptions.files as files_exc
from scrapers.lyrics_scraper import LyricsScraper
from utils.genutils import add_plural_ending, create_directory
from utils.logging.logutils import get_logger


class AZLyricsScraper(LyricsScraper):
    """Derived class for scraping and saving webpages locally

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
    logger : LoggingWrapper
        Used to log on the console and in a file.

    """

    VALID_DOMAIN = "www.azlyrics.com"
    """Only URLs from this domain will be processed (str)
    """

    def __init__(self, main_cfg, logger):
        super().__init__(main_cfg, logger)
        self.logger = get_logger(__name__,
                                 __file__,
                                 os.getcwd(),
                                 logger)

    def _scrape_artist_page(self, artist_filepath, artist_url):
        """Scrape the artist webpage.

        It crawls the artist webpage and scrapes any useful info to be added
        in the music database, such as the artist's name.

        The artist webpage is cached so that we reduce the number of HTTP
        requests to the lyrics website.

        Parameters
        ----------
        artist_filepath : str
            The file path of the artist webpage that is being scraped. The file
            path will be used to save the HTML document in cache.
        artist_url : str
            URL to the artist webpage that is being scraped.

        Raises
        ------
        HTTP404Error
            Raised if the server returns a 404 status code because the webpage
            is not found.
        OverwriteFileError
            Raised if an existing file is being overwritten and the flag to
            allow to overwrite is disabled.
        OSError
            Raised if an I/O related error occurs while writing the webpage on
            disk, e.g. the file doesn't exist.

        See Also
        --------
        azlyrics_scraper._scrape_lyrics_page : Scrape a lyrics webpage instead.

        """
        self.logger.debug(
            "Scraping the artist webpage {}".format(artist_url))
        # Load the webpage or save the webpage and retrieve its html
        html = None
        try:
            html, webpage_accessed = \
                self.saver.save_webpage(artist_filepath, artist_url, False)
        except (connec_exc.HTTP404Error,
                files_exc.OverwriteFileError,
                OSError) as e:
            # TODO: is it correct or `raise Exception(e)` or something else?
            raise e
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
            lyrics_filename = os.path.join(os.path.dirname(artist_filepath),
                                           os.path.basename(lyrics_url))
            self._scrape_lyrics_page(lyrics_filename, lyrics_url)

    def _scrape_lyrics_page(self, lyrics_filename, lyrics_url):
        """Scrape the lyrics webpage.

        It crawls the lyrics webpage and scrapes any useful info to be added
        in the music database, such as the song's title and the lyrics text.

        The lyrics webpage is cached so that we reduce the number of HTTP
        requests to the lyrics website.

        Parameters
        ----------
        lyrics_filename : str
            Filename of the lyrics webpage that is being scraped. The filename
            will be used to save the HTML document in cache.
        lyrics_url : str
            URL to the lyrics webpage that is being scraped.

        See Also
        --------
        azlyrics_scraper._scrape_artist_page : Scrape an artist webpage
                                               instead.

        """
        try:
            # Check first if the URL was already processed, i.e. is found in
            # the db
            self._check_url_in_db(lyrics_url)
            self.logger.debug(
                "Scraping the lyrics webpage {}".format(lyrics_url))
            # Load the webpage or save the webpage and retrieve its html
            html = None
            html, webpage_accessed = \
                self.saver.save_webpage(lyrics_filename, lyrics_url, False)
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
                    len(album_res), add_plural_ending(album_res)))
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
        except OSError as e:
            self.logger.exception(e)
            self.logger.warning(
                "Skipping the lyrics URL {}".format(lyrics_url))
        except (connec_exc.HTTP404Error,
                files_exc.OverwriteFileError,
                music_exc.MultipleAlbumError,
                music_exc.NonUniqueLyricsError,
                music_exc.NonUniqueAlbumYearError,
                music_exc.WrongAlbumYearError) as e:
            # TODO: `self.logger.exception(e)`? See also other places.
            self.logger.error(e)
            self.logger.warning(
                "Skipping the lyrics URL {}".format(lyrics_url))
        except (music_exc.MultipleLyricsURLError,
                music_exc.OverwriteSongError) as e:
            self.logger.info(e)
            self.logger.warning(
                "Skipping the lyrics URL {}".format(lyrics_url))

    def _process_url(self, url):
        """Process each URL defined in the YAML config file.

        The URLs can refer to an artist or lyrics webpage. In order to reduce
        the number of HTTP requests to the lyrics website, the URL is first
        checked if it is already in the database.

        Parameters
        ----------
        url : str
            URL to the artist's or lyrics webpage that will be scraped.

        Raises
        ------
        InvalidURLCategoryError
            Raised if the URL is not recognized as referring to neither an
            artist's nor a song's webpage.
            This is a custom exception.
        InvalidURLDomainError
            Raised if the URL is not from the domain wwww.azlyrics.com
            This is a custom exception.

        Notes
        -----
        The method saves the webpage HTML in cache and according to the type of
        the URL (artist or lyrics webpage), it calls the relevant method (
        _scrape_artist_page or _scrape_lyrics_page).

        There is a more robust parsing of the TLD: use a specialized library
        (e.g. `tldextract`). For example, `urlparse` will not be able to
        extract the right domain from a more complex URL such as
        'http://forums.news.cnn.com/'. On the other hand, `tldextract` will
        output 'cnn' which is correct.

        References
        ----------
        * `tldextract is a more efficient version of urlparse
        <https://stackoverflow.com/a/44022572>`_.

        * `Use urlparse but it might have some problems with some URLs
        <https://stackoverflow.com/a/44021937>`_

        * `Use urlparse and how to get the domain without the subdomain
        <https://stackoverflow.com/a/44113853>`_

        * `tldextract also works with emails and you install it with
        'pip install tldextract' <https://stackoverflow.com/a/45022556>`_

        * `Use os.path.basename if you want to extract a filename from the URL
        but it has its own problems with URLS having a query string
        <https://stackoverflow.com/a/51726087>`_

        """
        self.logger.info("Processing the URL {}".format(url))
        # Check first if the URL was already processed, i.e. is found in the db
        self._check_url_in_db(url)
        domain = urlparse(url).netloc
        # Create the name of the folder where the webpage will be saved
        dir_path = os.path.join(self.cache_filepath, domain)
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
            # TODO: add the three references
            self.logger.debug(
                "Checking if the URL {} is available".format(url))
            code = urlopen(url).getcode()
            self.logger.debug(
                "The URL {} is up. Status code: {}".format(url, code))
            self.logger.debug("Validating the URL's domain")

            # Validate URL's domain
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
            except FileExistsError as e:
                self.logger.warning(e)

        # Check if the azlyrics URL belongs to a lyrics or artist
        # and start the scraping of the actual webpage with BeautifulSoup
        if urlparse(url).path.startswith('/lyrics/'):
            self.logger.debug(
                "The URL {} refers to a lyrics' webpage".format(url))
            self._scrape_lyrics_page(webpage_filename, url)
        elif urlparse(url).path.startswith('/19/') or \
                urlparse(url).path[1].isalpha():
            # NOTE: webpages of artists' names that start with a number are
            # placed within the directory /19/
            # e.g. https://www.azlyrics.com/19/50cent.html
            self.logger.debug(
                "The URL {} refers to an artist's webpage".format(url))
            self._scrape_artist_page(webpage_filename, url)
        else:
            raise music_exc.InvalidURLCategoryError(
                "The URL {} is not recognized as referring to neither "
                "an artist's nor a song's webpage".format(url))
