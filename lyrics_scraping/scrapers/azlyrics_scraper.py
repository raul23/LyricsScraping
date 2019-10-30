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
import re
import signal
import time
from collections import namedtuple
from difflib import get_close_matches
from logging import NullHandler
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

import lyrics_scraping.exceptions
import pyutils.exceptions
from lyrics_scraping.scrapers.lyrics_scraper import Lyrics, LyricsScraper
from lyrics_scraping.utils import add_plural_ending
from pyutils.logutils import get_error_msg

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


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
        self.search_url = "https://search.azlyrics.com/search.php"
        # TODO: explain that p is for page, w is for I suppose weight
        # (albums, artists, songs), q is for query, ...
        self._search_url_params = {'q': "", 'w': "", 'p': 1}
        # Warning message taken from https://search.azlyrics.com/search.php
        self.no_results_warning = "Sorry, your search returned <color>no " \
                                  "results</color>. Try to compose less " \
                                  "restrictive search query or check spelling."

    def get_lyrics_from_album(self, album_title, artist_name=None,
                              max_songs=None):
        """TODO

        Parameters
        ----------
        album_title
        artist_name
        max_songs

        Returns
        -------

        """
        # TODO: explain
        return self._get_lyrics("album", album_title, artist_name, max_songs)

    def get_song_lyrics(self, song_title, artist_name=None):
        """TODO

        Parameters
        ----------
        song_title
        artist_name

        Returns
        -------

        """
        # TODO: explain
        if artist_name:
            query = "{} by {}".format(song_title, artist_name)
        else:
            query = song_title
            artist_name = ""
        tags = self._send_song_search_request(query, "songs")
        logger.debug("<color>Found {} song results (page 1)"
                     "</color>".format(len(tags)))
        if not tags and artist_name:
            logger.debug("<color>We will try to send the song request with the "
                         "song title only</color>")
            tags = self._send_song_search_request(song_title, "songs")
            logger.debug("<color>Found {} song results (page 1)"
                         "</color>".format(len(tags)))
        if tags:
            search_results = self._get_search_results(tags)
            search_results_str = search_results.search_results_str
            search_results_list = search_results.search_results_list
            if self.interactive:
                num = self._ask_user_for_search_result(search_results_str,
                                                       search_results_list)
                tag = tags[num - 1]
            else:
                # No interaction
                logger.debug(search_results_str[:-1])
                if self.best_match:  # Select best match
                    word = song_title + " by " + artist_name if artist_name else song_title
                    result_index = self._select_best_match(word,
                                                           search_results_list)
                    if result_index:
                        tag = tags[result_index]
                    else:
                        return None
                else:  # No match
                    # We choose the first search result
                    logger.debug("<color>Choosing the first search result:"
                                 "</color> {}".format(search_results_list[0]))
                    tag = tags[0]
            url = tag.find("a").attrs['href']
            logger.debug("Song's URL: {}".format(url))
            logger.debug("Getting lyrics from song's webpage ...")
            return self._get_lyrics_from_url(url)
        else:  # tags is empty
            logger.warning(self.no_results_warning)
            return None

    def handler(self, signum, frame):
        print('Signal handler called with signal', signum)
        raise TimeoutError("{} seconds had passed and no search result "
                           "selected.".format(self.delay_interactive))

    @staticmethod
    def _get_search_results(which, tags):
        """TODO

        Parameters
        ----------
        tags

        Returns
        -------

        """
        search_results_str = "\n"
        # NOTE: we start numbering at 1 instead of 0
        search_results_list = []
        for i, t in enumerate(tags, start=1):
            if which == "songs":
                title, artist = t.select("b")
                title = title.text
                artist = artist.text
                search_results_list.append(title + " by " + artist)
                search_results_str += "[{}] <color>{}</color> by " \
                                      "{}\n".format(i, title, artist)
            else:
                # Text has the name of the artist followed by the name of the
                # album, e.g. Depeche Mode - Speak & Spell
                text = t.select_one("b").text
                search_results_list.append(text)
                search_results_str += "[{}] <color>{}</color>\n".format(i, text)
        search_results = namedtuple("search_results",
                                    "search_results_str search_results_list")
        search_results.search_results_str = search_results_str
        search_results.search_results_list = search_results_list
        return search_results

    def _ask_user_for_search_result(self, which, search_results_str,
                                    search_results_list):
        """TODO

        Parameters
        ----------
        search_results_str
        search_results_list

        Returns
        -------

        """
        # Ask the user to select the search result that best matches
        # their search query
        logger.info("\n\n{} RESULTS: {}".format(which.upper(), search_results_str))
        if len(search_results_list) > 1:
            msg = "Choose a number from [{}] to [{}] or Type 'n' for None: " \
                  "".format(1, len(search_results_list))
            retval = self._multiple_search_result_case(msg,
                                                       len(search_results_list))
        else:
            msg = "Only one search result.\nType 'y' to accept it or 'n' to " \
                  "reject it: "
            retval = self._single_search_result_case(msg)
        if isinstance(retval, int):
            # Since we started numbering at 1 but list index starts at 0
            logger.info("<color>Search result #{} selected:</color> "
                        "{}".format(retval, search_results_list[retval-1]))
        else:
            logger.warning("<color>No search result selected</color>")
        return retval

    def _multiple_search_result_case(self, msg, nb_results):
        """TODO

        Parameters
        ----------
        msg
        nb_results

        Returns
        -------

        """
        # logger.debug("<color>{}</color>".format(msg))
        signal.signal(signal.SIGALRM, self.handler)
        while True:
            answer = ""
            try:
                signal.alarm(self.delay_interactive)
                answer = input(msg)
                if answer.lower() == 'n':
                    logger.debug("No search result selected")
                    answer = answer.lower()
                else:
                    answer = int(answer)
            except ValueError as e:
                # e.g. float or string
                # Ask again
                logger.debug("<color>{}</color>".format(e))
            except TimeoutError as e:
                logger.warning("<color>{}</color>".format(e))
                logger.warning("<color>The first search result will be selected"
                               "</color>")
                answer = 1
                time.sleep(3)
            finally:
                if answer == 'n' or answer in range(1, nb_results + 1):
                    # Good input. Break from loop
                    break
                else:
                    # Ask again
                    logger.debug("Ask again!")
        signal.alarm(0)
        num = None if answer == 'n' else answer
        return num

    def _single_search_result_case(self, msg):
        """TODO

        Parameters
        ----------
        msg
        search_results

        Returns
        -------

        """
        # logger.debug("<color>{}</color>".format(msg))
        signal.signal(signal.SIGALRM, self.handler)
        while True:
            answer = ""
            try:
                signal.alarm(self.delay_interactive)
                answer = str(input(msg)).lower()
            except ValueError as e:
                # e.g. number
                # Ask again
                logger.debug("<color>{}</color>".format(e))
            except TimeoutError as e:
                logger.warning("<color>{}</color>".format(e))
                logger.warning("<color>The only search result will be selected"
                               "</color>")
                answer = 'y'
                time.sleep(3)
            finally:
                if answer in ['y', 'n']:
                    break
                else:
                    # Ask again
                    logger.debug("Ask again!")
        # Disable the alarm
        signal.alarm(0)
        num = 1 if answer == 'y' else None
        return num

    def _select_best_match(self, word, possibilities):
        """TODO

        Parameters
        ----------
        word
        possibilities

        Returns
        -------

        """
        # TODO: update following comment since we might also be using for albums and artists
        # We choose the best song title and artist name from the
        # search results that match the user's given song title and
        # artist name
        matches = get_close_matches(word, possibilities)
        if matches:
            logger.debug(
                "<color>Found {} match{} for '{}':</color> {}".format(
                    len(matches),
                    add_plural_ending(matches, "es"),
                    word,
                    ", ".join(matches)))
            result_index = possibilities.index(matches[0])
            logger.debug("<color>Matching your search query '{}' with"
                         " '{}'</color>".format(word, matches[0]))
            logger.debug("<color>Search result #{} selected:</color>"
                         " {}".format(result_index + 1,
                                      possibilities[result_index]))
            return result_index
        else:
            logger.warning("<color>No match found for '{}'"
                           "</color>".format(word))
            logger.warning(self.no_results_warning)
            return None

    def _send_search_request(self, which, search_query):
        """TODO

        Parameters
        ----------
        query
        which

        Returns
        -------

        """
        # TODO: explain
        self._search_url_params['q'] = search_query
        self._search_url_params['w'] = which + "s"
        logger.debug("<color>Sending search request ...</color>")
        html = self.webcache.get_webpage(self.search_url,
                                         self._search_url_params)
        soup = BeautifulSoup(html, 'lxml')
        tags = soup.select("td.visitedlyr")
        return tags

    def _get_lyrics(self, which, which_title, artist_name=None, max_songs=None):
        """TODO

        Parameters
        ----------
        which
        which_title
        artist_name
        max_songs

        Returns
        -------

        """
        # TODO: explain
        if artist_name:
            query = "{} by {}".format(which_title, artist_name)
        else:
            query = which_title
            artist_name = ""
        tags = self._send_search_request(which, query)
        logger.debug("<color>Found {} {} results (page 1)"
                     "</color>".format(len(tags), which))
        if not tags and artist_name:
            logger.debug("<color>We will try to send the {} request with the "
                         "{} title only</color>".format(which, which))
            tags = self._send_search_request(which, which_title)
            logger.debug("<color>Found {} {} results (page 1)"
                         "</color>".format(len(tags), which))
        if tags:
            search_results = self._get_search_results(which, tags)
            search_results_str = search_results.search_results_str
            search_results_list = search_results.search_results_list
            if self.interactive:
                num = self._ask_user_for_search_result(which,
                                                       search_results_str,
                                                       search_results_list)
                if num is None:
                    # No search result selected
                    return None
                else:
                    assert_msg = "The selected value ({}) must be an " \
                                 "integer".format(num)
                    assert isinstance(num, int), assert_msg
                    tag = tags[num - 1]
            else:
                # No interaction
                logger.debug(search_results_str[:-1])
                if self.best_match:  # Select best match
                    if artist_name:
                        # Album and song search results are displayed differently
                        if which == "album":
                            word = "{} - {}".format(artist_name, which_title)
                        else:
                            word = "{} by {}".format(which_title, artist_name)
                    else:
                        word = which_title
                    result_index = self._select_best_match(word,
                                                           search_results_list)
                    if result_index:
                        tag = tags[result_index]
                    else:
                        return None
                else:  # No match
                    # We choose the first search result
                    logger.debug("<color>Choosing the first search result:"
                                 "</color> {}".format(search_results_list[0]))
                    tag = tags[0]
            url = tag.find("a").attrs['href']
            logger.debug("{}'s URL: {}".format(which, url))
            logger.debug("Getting lyrics from {}'s webpage ...".format(which))
            return self._get_lyrics_from_url(url, max_songs)
        else:  # tags is empty
            logger.warning(self.no_results_warning)
            return None

    def _get_lyrics_from_url(self, url, max_songs=None):
        """TODO

        Different scraping methods are called depending on the type of webpage:
        :meth:`._scrape_artist_page()` if it is an artist webpage and
        :meth:`_scrape_lyrics_page()` if it is a lyrics webpage.

        Parameters
        ----------
        url : str
            URL of the webpage to be scraped.

        Returns
        -------

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
        # and start the scraping of the webpage
        if urlparse(url).path.startswith('/lyrics/'):
            # Lyrics URL
            logger.debug("The URL refers to a lyrics webpage: {}".format(url))
            # TODO: raise error from _scrape_lyrics_page
            return self._scrape_lyrics_page(url)
        elif urlparse(url).path.startswith('/19/') or \
                urlparse(url).path[1].isalpha():
            # Artist URL
            # NOTE: artists' names that start with a number have their webpages
            # placed within the directory /19/
            # e.g. https://www.azlyrics.com/19/50cent.html
            logger.debug("The URL {} refers to an artist's webpage".format(url))
            # TODO: raise error from _scrape_artist_page
            return self._scrape_artist_page(url, max_songs)
        else:
            # Bad URL
            raise lyrics_scraping.exceptions.InvalidURLCategoryError(
                "The URL {} is not recognized as referring to either "
                "an artist's or a lyrics webpage".format(url))

    def _scrape_artist_page(self, artist_url, max_songs=None):
        """Scrape the artist webpage.

        It crawls the artist webpage and scrapes any useful info to be saved,
        such as the artist's name.

        The artist webpage is cached so that we reduce the number of HTTP
        requests to the lyrics website.

        Parameters
        ----------
        artist_url : str
            URL to the artist webpage that is being scraped.

        Raises
        ------
        HTTP404Error
            Raised if the server returns a 404 status code because the webpage
            is not found. TODO: add link to custom exception

        See Also
        --------
        _scrape_lyrics_page : Scrapes a lyrics webpage instead.

        """
        if max_songs:
            logger.debug("<color>Per album's max_songs(={}) used"
                         "</color>".format(max_songs))
            logger.info("The <color>first {} songs</color> from the album will "
                        "be processed".format(max_songs))
        else:
            if self.max_songs:
                max_songs = self.max_songs
                logger.debug("<color>Global max_songs(={}) used"
                             "</color>".format(max_songs))
                logger.info("The <color>first {} songs</color> from the album "
                            "will be processed".format(max_songs))
            else:
                logger.info("<color>All songs</color> from the album will be processed")
        # Retrieve the webpage's HTML
        html = None
        try:
            # Cache the webpage and retrieve its html content
            html = self.webcache.get_webpage(artist_url)
        except (requests.RequestException,
                pyutils.exceptions.HTTP404Error):
            raise
        logger.debug("Scraping the artist webpage {}".format(artist_url))
        soup = BeautifulSoup(html, 'lxml')
        # Get the name of the artist
        # The name of the artist is found in the title of the artist's webpage
        # as "Artist name Lyrics"
        artist_name = soup.title.text.split(' Lyrics')[0]
        # Save artist data
        # self._save_artist(artist_name)
        if ".html#" in artist_url:
            # Case where the URL points to a specific album
            # Get div's id from URL
            id_ = artist_url.split("#")[1]
            # Get all <div id=id_>'s siblings
            siblings = soup.find("div", id=id_).find_next_siblings()
            # Only get those siblings that are related to the album associated
            # with the given id
            anchors = []
            for sibling in siblings:
                if sibling.get('href'):
                    anchors.append(sibling)
                elif sibling.get('class') and 'album' in sibling.get('class'):
                    break
                else:
                    continue
        else:
            # Case where the URL refers to all albums from the given artist
            # Get the list of lyrics URLs from the given artist
            # The URLs will be found as values to anchor's href attributes
            # e.g. <a href="../lyrics/artist_name/song_title.html" ... >
            anchors = soup.find_all("a", href=re.compile("^../lyrics"))
        logger.debug("<color>There are in total {} lyrics URLs"
                     "</color>".format(len(anchors)))
        if max_songs:
            anchors = anchors[:max_songs]
        # Process each lyrics' url
        logger.info("There are <color>{} lyrics URLs</color> to process for "
                    "the given artist".format(len(anchors)))
        all_lyrics = []
        for i, a in enumerate(anchors):
            # Get URL from the anchor's href attribute
            lyrics_url = a.attrs['href']
            logger.debug("<color>{}</color>".format("-"*100))
            logger.debug("<color>#{} Processing the lyrics URL "
                         "{}</color>".format(i+1, lyrics_url))
            logger.debug("<color>Processing the anchor '{}'</color>".format(a))
            # Check if the lyrics' URL is relative to the current artist's URL
            logger.debug("<color>Checking if the URL {} is relative"
                         "</color>".format(lyrics_url))
            if lyrics_url.startswith('../'):
                logger.debug("<color>The URL {} is relative"
                             "</color>".format(lyrics_url))
                # Complete the relative URL by adding the scheme and hostname
                # [scheme]://[hostname][path]
                # NOTE: lyrics_url[2:] results in removing the two dots at the
                # beginning of the lyrics URL since it is a relative URL
                parsed_url = urlparse(artist_url)
                lyrics_url = '{}://{}{}'.format(parsed_url.scheme,
                                                parsed_url.hostname,
                                                lyrics_url[2:])
            skip_url = False
            error = None
            try:
                lyrics = self._scrape_lyrics_page(lyrics_url)
            except OSError as e:
                logger.exception(e)
                error = e
                skip_url = True
            except (pyutils.exceptions.HTTP404Error,
                    lyrics_scraping.exceptions.CurrentSessionURLError,
                    lyrics_scraping.exceptions.MultipleAlbumError,
                    lyrics_scraping.exceptions.MultipleLyricsURLError,
                    lyrics_scraping.exceptions.NonUniqueLyricsError,
                    lyrics_scraping.exceptions.NonUniqueAlbumYearError,
                    lyrics_scraping.exceptions.OverwriteSongError,
                    lyrics_scraping.exceptions.WrongAlbumYearError) as e:
                logger.error(e)
                error = e
                skip_url = True
            else:
                logger.debug("Lyrics URL successfully processed: "
                             "{}".format(lyrics_url))
                self.good_urls.add(lyrics_url)
                all_lyrics.append(lyrics)
            finally:
                if skip_url:
                    self._add_skipped_url(lyrics_url, get_error_msg(error))
        return all_lyrics

    def _scrape_lyrics_page(self, lyrics_url):
        """Scrape the lyrics webpage.

        It crawls the lyrics webpage and scrapes any useful info to be saved,
        such as the song's title and the lyrics text.

        The lyrics webpage is cached so that we reduce the number of HTTP
        requests to the lyrics website.

        Parameters
        ----------
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
        # Check first if the URL was already processed, e.g. is found in the db
        if self._url_already_processed(lyrics_url) in [0, 2]:
            # Cache the webpage and retrieve its html content
            html = self.webcache.get_webpage(lyrics_url)
            logger.debug("Scraping the lyrics webpage @ {}".format(lyrics_url))
            soup = BeautifulSoup(html, 'lxml')
            # Get the following data from the lyrics webpage:
            # - the title of the song
            # - the name of the artist
            # - the text of the song
            # - the album title the song comes from
            # - the year the album was released
            # TODO: explain
            song_title = soup.title.text.split('- ')[1].split(' Lyrics')[0]
            artist_name = soup.title.text.split(' -')[0]
            lyrics_result = soup.find_all("div", class_="", id="")
            logger.debug("<color>Song title extracted:</color> "
                         "{}".format(song_title))
            logger.debug("<color>Artist name extracted:</color> "
                         "{}".format(artist_name))
            # Sanity check on lyrics: lyrics are ONLY found within a <div>
            # without class and id
            if len(lyrics_result) != 1:
                raise lyrics_scraping.exceptions.NonUniqueLyricsError(
                    "Lyrics extraction scheme broke: no lyrics found or more "
                    "than one lyrics were found")
            lyrics_text = lyrics_result[0].text.strip()
            logger.debug("<color>Lyrics text extracted</color>")
            album_result = soup.find_all("div",
                                         class_="panel songlist-panel noprint")
            logger.debug("<color>{} album{} found</color>".format(
                len(album_result), add_plural_ending(album_result)))
            if len(album_result) == 0:
                # No album found
                logger.debug("No album found in the lyrics webpage: "
                             "{}".format(lyrics_url))
                # Add empty string to the album result to notify that no album
                # was found when processing each album in the result
                album_result.append("")
            # Process each album from the album result
            for album in album_result:
                if album:
                    # The album's title and year are found in a line like this:
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
                        raise lyrics_scraping.exceptions.NonUniqueAlbumYearError(
                            "The album's year extraction doesn't result in a "
                            "UNIQUE number")
                    # Sanity check on the album's year: the year should be a number
                    # with four digits
                    if not (len(year_result[0]) and year_result[0].isdecimal()):
                        raise lyrics_scraping.exceptions.WrongAlbumYearError(
                            "The Album's year extraction scheme broke: the year "
                            "'{}' is not a number with four digits".format(
                                year_result[0]))
                    song_year = year_result[0]
                    logger.debug("<color>Album title extracted:</color> "
                                 "{}".format(album_title))
                    logger.debug("<color>Song year extracted:</color> "
                                 "{}".format(song_year))
                else:
                    # No album found thus give empty strings to its title and year
                    album_title = ""
                    song_year = ""
                lyrics = Lyrics(song_title=song_title,
                                artist_name=artist_name,
                                album_title=album_title,
                                lyrics_url=lyrics_url,
                                lyrics_text=lyrics_text,
                                year=song_year)
                # TODO: add these lines in a method
                """
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
                """
                return lyrics
        else:
            # Skip URL
            logger.warning("<color>The URL will be skipped because it was "
                           "already processed:</color> {}".format(lyrics_url))
            return None
