"""Module that defines the derived class for scraping artist and lyrics
webpages from `www.azlyrics.com`_

:class:`AZLyricsScraper` is derived from the base class
:class:`~scrapers.lyrics_scraper.LyricsScraper`. :class:`AZLyricsScraper`
crawls and scrapes artist and lyrics webpages from `www.azlyrics.com`_ for
useful data to be saved, such as the artist's name, the album's title, and the
lyrics text.

The actual saving of the data in a dictionary and a database is done by the
base class :class:`~scrapers.lyrics_scraper.LyricsScraper`.

Notes
-----
See the structure of the music database as defined in the `music.sql schema`_.

.. _www.azlyrics.com: https://www.azlyrics.com/
.. _music.sql schema: https://bit.ly/2kIMYvn

"""

import logging
import os
import re
from logging import NullHandler
from urllib.parse import urlparse
# Third-party modules
from bs4 import BeautifulSoup
# Custom modules
import lyrics_scraping.scrapers.exceptions as scraper_exc
import pyutils.exceptions.connection as connec_exc
import pyutils.exceptions.files as files_exc
from lyrics_scraping.scrapers.lyrics_scraper import LyricsScraper
from pyutils.genutils import add_plural_ending
from pyutils.log.logging_wrapper import LoggingWrapper
from pyutils.logutils import get_error_msg


logging.getLogger(__name__).addHandler(NullHandler())


class AZLyricsScraper(LyricsScraper):
    """Derived class from :class:`~scrapers.lyrics_scraper.LyricsScraper` for
    scraping artist and lyrics webpages from `www.azlyrics.com`_

    This class is responsible for scraping webpages from `www.azlyrics.com`_ for
    any relevant data about albums, artists, and songs.

    The scraped data is then saved in a dictionary and a database (if one was
    configured). The base class :class:`~scrapers.lyrics_scraper.LyricsScraper`
    is responsible for handling the saving of the scraped data.

    The :meth:`__init__` method extends the superclass's constructor by getting
    its own logger.

    Attributes
    ----------
    logger : logging.Logger
        Logger for logging to console and file.


    .. note::

       See the structure of the music database as defined in the `music.sql
       schema`_.

    .. important::

       :class:`AZLyricsScraper`'s parameters are those from its parent class
       :ref:`LyricsScraper <LyricsScraperParametersLabel>`.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        # Experimental option: add color to log messages
        if os.environ.get('COLOR_LOGS'):
            self.logger = LoggingWrapper(self.logger,
                                         os.environ.get('COLOR_LOGS'))

    def _scrape_webpage(self, url, webpage_filepath):
        """Scrape a given webpage and save the scraped data.

        Different scraping methods are called depending on the type of webpage:
        :meth:`._scrape_artist_page()` if it is an artist webpage and
        :meth:`_scrape_lyrics_page()` if it is a lyrics webpage.

        Parameters
        ----------
        url : str
            URL of the webpage to be scraped.
        webpage_filepath : str
            The path of the webpage where its HTML will be saved if the cache
            is used.

        Raises
        ------
        InvalidURLCategoryError
            Raised if the URL is not recognized as referring to neither an
            artist's nor a song's webpage.

        See Also
        --------
        _scrape_artist_page : Scrapes an artist webpage.
        _scrape_lyrics_page : Scrapes a lyrics webpage.

        """
        # Check if the azlyrics URL belongs to a lyrics or artist
        # and start the scraping of the actual webpage with BeautifulSoup
        if urlparse(url).path.startswith('/lyrics/'):
            # Lyrics URL
            self.logger.debug("The URL {} refers to a lyrics "
                              "webpage".format(url))
            self._scrape_lyrics_page(webpage_filepath, url)
        elif urlparse(url).path.startswith('/19/') or \
                urlparse(url).path[1].isalpha():
            # Artist URL
            # NOTE: artists' names that start with a number have their webpages
            # placed within the directory /19/
            # e.g. https://www.azlyrics.com/19/50cent.html
            self.logger.debug("The URL {} refers to an artist's "
                              "webpage".format(url))
            self._scrape_artist_page(webpage_filepath, url)
        else:
            # Bad URL
            raise scraper_exc.InvalidURLCategoryError(
                "The URL {} is not recognized as referring to neither "
                "an artist's nor a lyrics webpage".format(url))

    def _scrape_artist_page(self, artist_filepath, artist_url):
        """Scrape the artist webpage.

        It crawls the artist webpage and scrapes any useful info to be saved,
        such as the artist's name.

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
            is not found. TODO: add link to custom exception
        OverwriteFileError
            Raised if an existing file is being overwritten and the flag to
            allow to overwrite is disabled. TODO: add link to custom exception
        OSError
            Raised if an I/O related error occurs while writing the webpage on
            disk, e.g. the file doesn't exist.

        See Also
        --------
        _scrape_lyrics_page : Scrapes a lyrics webpage instead.

        """
        self.logger.debug("Scraping the artist webpage {}".format(artist_url))
        # Load the webpage or save the webpage and retrieve its html
        html = None
        try:
            # Save the webpage and retrieve its html content
            html = self._get_html(artist_filepath, artist_url)
        except (connec_exc.HTTP404Error,
                files_exc.OverwriteFileError,
                OSError) as e:
            # TODO: is it correct or `raise Exception(e)` or something else?
            raise e
        bs_obj = BeautifulSoup(html, 'lxml')
        # Get the name of the artist
        # The name of the artist is found in the title of the artist's webpage
        # as "Artist name Lyrics"
        artist_name = bs_obj.title.text.split(' Lyrics')[0]
        # Save artist data
        self._save_artist(artist_name)
        # Get the list of lyrics URLs from the given artist
        # The URLs will be found as values to anchor's href attributes
        # e.g. <a href="../lyrics/artist_name/song_title.html" ... >
        anchors = bs_obj.find_all("a", href=re.compile("^../lyrics"))
        # Process each lyrics' url
        self.logger.info("There are {} lyrics URLs to process for the given "
                         "artist".format(len(anchors)))
        for i, a in enumerate(anchors):
            # Get URL from the anchor's href attribute
            lyrics_url = a.attrs['href']
            self.logger.info("#{} Processing the lyrics URL "
                             "{}".format(i+1, lyrics_url))
            self.logger.debug("Processing the anchor '{}'".format(a))
            # Check if the lyrics' URL is relative to the current artist's URL
            self.logger.debug("Checking if the URL {} is "
                              "relative".format(lyrics_url))
            if lyrics_url.startswith('../'):
                self.logger.debug("The URL {} is relative".format(lyrics_url))
                # Complete the relative URL by adding the scheme and hostname
                # [scheme]://[hostname][path]
                # NOTE: lyrics_url[2:] results in removing the two dots at the
                # beginning of the lyrics URL since it is a relative URL
                parsed_url = urlparse(artist_url)
                lyrics_url = '{}://{}{}'.format(parsed_url.scheme,
                                                parsed_url.hostname,
                                                lyrics_url[2:])
            # Build the filename where the lyrics webpage will be saved
            lyrics_filename = os.path.join(os.path.dirname(artist_filepath),
                                           os.path.basename(lyrics_url))
            skip_url = True
            error = None
            try:
                self._scrape_lyrics_page(lyrics_filename, lyrics_url)
            except OSError as e:
                self.logger.exception(e)
                error = e
            except (connec_exc.HTTP404Error,
                    files_exc.OverwriteFileError,
                    scraper_exc.CurrentSessionURLError,
                    scraper_exc.MultipleAlbumError,
                    scraper_exc.MultipleLyricsURLError,
                    scraper_exc.NonUniqueLyricsError,
                    scraper_exc.NonUniqueAlbumYearError,
                    scraper_exc.OverwriteSongError,
                    scraper_exc.WrongAlbumYearError) as e:
                self.logger.error(e)
                error = e
            else:
                skip_url = False
            finally:
                if skip_url:
                    self._add_skipped_url(lyrics_url, get_error_msg(error))
                else:
                    self.logger.debug("Lyrics URL successfully processed: "
                                      "{}".format(lyrics_url))
                    self.good_urls.add(lyrics_url)

    def _scrape_lyrics_page(self, lyrics_filepath, lyrics_url):
        """Scrape the lyrics webpage.

        It crawls the lyrics webpage and scrapes any useful info to be saved,
        such as the song's title and the lyrics text.

        The lyrics webpage is cached so that we reduce the number of HTTP
        requests to the lyrics website.

        Parameters
        ----------
        lyrics_filepath : str
            File path of the lyrics webpage that is being scraped. The filename
            will be used to save the HTML document in cache.
        lyrics_url : str
            URL to the lyrics webpage that is being scraped.

        Raises
        ------
        NonUniqueLyricsError
            Raised if the lyrics extraction scheme broke: no lyrics found or
            more than one lyrics were found on the lyrics webpage.
        NonUniqueAlbumYearError
            Raised if no album's year or more than one album's year were found
            on the lyrics webpage.
        WrongAlbumYearError
            Raised if the album's year is not a number with four digits.

        See Also
        --------
        _scrape_artist_page : Scrapes an artist webpage instead.

        """
        self.logger.debug("Scraping the lyrics webpage {}".format(lyrics_url))
        # Check first if the URL was already processed, e.g. is found in the db
        self._check_url_if_processed(lyrics_url)
        # Save the webpage and retrieve its html content
        html = self._get_html(lyrics_filepath, lyrics_url)
        bs_obj = BeautifulSoup(html, 'lxml')
        # Get the following data from the lyrics webpage:
        # - the title of the song
        # - the name of the artist
        # - the text of the song
        # - the album title the song comes from
        # - the year the album was released
        # TODO: explain
        song_title = bs_obj.title.text.split('- ')[1].split(' Lyrics')[0]
        artist_name = bs_obj.title.text.split(' -')[0]
        lyrics_result = bs_obj.find_all("div", class_="", id="")
        # Sanity check on lyrics: lyrics are ONLY found within a <div>
        # without class and id
        if len(lyrics_result) != 1:
            raise scraper_exc.NonUniqueLyricsError(
                "Lyrics extraction scheme broke: no lyrics found or more "
                "than one lyrics were found")
        lyrics_text = lyrics_result[0].text.strip()
        album_result = bs_obj.find_all("div",
                                       class_="panel songlist-panel noprint")
        self.logger.debug("{} album{} found".format(
            len(album_result), add_plural_ending(album_result)))
        if len(album_result) == 0:
            # No album found
            self.logger.debug("No album found in the lyrics webpage "
                              "{}".format(lyrics_url))
            # Add empty string to the album result to notify that no album
            # was found when processing each album in the result
            album_result.append("")
        # Process each album from the album result
        for album in album_result:
            if album:
                # The album's title and year is found in a line like this:
                # album: <b>"Album title"</b> (1981)<br/><br/>
                # And this line is found within a <div> tag:
                # <div class="panel songlist-panel noprint">
                # NOTE: .contents returns all the tag's children
                # Thus, .contents[1] returns <b>"Album title"</b>
                # album.contents[1].text returns '"Album title"', thus we
                # strip to remove the double quotes and get a clean string
                # representation like 'Album title'. If we don't do that, then
                # we will store the album titles in the database within double
                # quotes, e.g. "New Life"
                album_title = album.contents[1].text.strip('"')
                # .contents[2] returns ' (1981)'. Thus, we use a regex to
                # extract only the numbers from the string.
                year_result = re.findall(r'\d+', album.contents[2])
                # Sanity check on the album's year: there should be only one
                # album's year extracted
                if len(year_result) != 1:
                    # 0 or more than 1 album's year found
                    raise scraper_exc.NonUniqueAlbumYearError(
                        "The album's year extraction doesn't result in a "
                        "UNIQUE number")
                # Sanity check on the album's year: the year should be a number
                # with four digits
                if not (len(year_result[0]) and year_result[0].isdecimal()):
                    raise scraper_exc.WrongAlbumYearError(
                        "The Album's year extraction scheme broke: the year "
                        "'{}' is not a number with four digits".format(
                            year_result[0]))
                song_year = year_result[0]
            else:
                # No album found thus give empty strings to its title and year
                album_title = ""
                song_year = ""
            # Save the relevant scraped data
            self._save_artist(artist_name)
            self._save_album(album_title=album_title,
                             artist_name=artist_name,
                             year=song_year)
            self._save_song(song_title=song_title,
                            artist_name=artist_name,
                            album_title=album_title,
                            lyrics_url=lyrics_url,
                            lyrics=lyrics_text,
                            year=song_year)
