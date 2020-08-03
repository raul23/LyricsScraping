"""Module that defines the derived class for scraping artist and lyrics
webpages from `www.azlyrics.com`_

:class:`AZLyricsScraper` is derived from the base class
:class:`~scrapers.lyrics_scraper.LyricsScraper`. :class:`AZLyricsScraper`
crawls and scrapes artist and lyrics webpages from `www.azlyrics.com`_ for
useful data to be saved, such as the artist's name, the album title, and the
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

from bs4 import BeautifulSoup

import lyrics_scraping.exceptions
from lyrics_scraping.scrapers.lyrics_scraper import Album, Lyrics, LyricsScraper
from lyrics_scraping.utils import plural

import ipdb

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

    # TODO: change name to get_album_songs() or search_album()
    def get_lyrics_from_album(self, album_title, artist_name=None,
                              max_songs=None, choose_random=False):
        """TODO

        Parameters
        ----------
        album_title
        artist_name
        max_songs
        choose_random

        Returns
        -------
        TODO

        """
        # TODO: explain
        return self._get_lyrics("album", album_title, artist_name, max_songs,
                                choose_random)

    # TODO: change name to get_artist_songs() or search_artist()
    def get_lyrics_from_artist(self, artist_name, max_songs=None,
                               year_after=None, year_before=None,
                               include_unknown_year=False, choose_random=False):
        """TODO

        Parameters
        ----------
        artist_name
        max_songs
        year_after
        year_before
        include_unknown_year
        choose_random

        Returns
        -------
        TODO

        Raises
        ------
        ValueError
            TODO

        """
        # TODO: explain
        try:
            years = self._check_years(year_after, year_before)
            return self._get_lyrics("artist", None, artist_name, max_songs,
                                    year_after=years.year_after,
                                    year_before=years.year_before,
                                    include_unknown_year=include_unknown_year,
                                    choose_random=choose_random)
        except ValueError:
            raise

    # TODO: change name to get_song() or search_song()
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
        return self._get_lyrics("song", song_title, artist_name)

    def handler(self, signum, frame):
        """TODO

        Parameters
        ----------
        signum
        frame

        Returns
        -------

        """
        # TODO: explain
        print('Signal handler called with signal', signum)
        raise TimeoutError("{} seconds had passed and no search result "
                           "selected.".format(self.delay_interactive))

    def _add_songs_from_same_album(self, div, artist_url, albums):
        """TODO

        Parameters
        ----------
        div
        artist_url
        albums

        Raises
        ------
        TODO

        """
        # TODO: explain
        # The <div> tag refers to an album
        # Get the album title
        album_title = self._get_album_title_from_div_tag(div)
        # Get the album year
        year_result = re.findall(r'\((\d+)\)', div.text)
        # Sanity check the extracted album year
        try:
            self._check_album_year(year_result)
        except (lyrics_scraping.exceptions.NonUniqueAlbumYearError,
                lyrics_scraping.exceptions.WrongAlbumYearError) as e:
            # TODO: add error in albums dict
            if self.ignore_errors:
                logger.error(e)
                logger.warning("Skipping the album '{}'".format(
                    album_title))
            else:
                raise e
        else:
            # Valid album year
            album_year = int(year_result[0])
            logger.debug("The album <color>'{}'</color> ({}) will "
                         "be <color>added</color>".format(
                          album_title, album_year))
            # Get all songs from the given album
            # Only get those songs (siblings) that are related to the given album
            siblings = div.find_next_siblings()
            # TODO: [siblings_refactor]
            for index, sibling in enumerate(siblings, start=1):
                # A song must be associated with an <a href="..."> tag
                # Example:
                # <a href="../lyrics/depechemode/goingbackwards.html"
                # target="_blank"> Going Backwards</a>
                if sibling.get('href'):
                    self._update_albums_dict(albums, sibling, album_title,
                                             album_year, artist_url)
                elif sibling.get('class') and \
                        'album' in sibling.get('class'):
                    # We arrived at the beginning of another album. Thus, we must
                    # exit from the 'for loop' since we finished adding all songs
                    # from the given album
                    # Example:
                    # <div class="album" id="7852">album: <b>"A Broken Frame"
                    # </b> (1982)</div>
                    break
                else:
                    # Neither a song nor an album, e.g. <br/>
                    # Thus, we skip the current sibling
                    continue
            if albums.get(album_title):
                logger.debug("<color>{} songs added</color> from <color>'{}'"
                             "</color>".format(
                              len(albums[album_title]['songs']), album_title))

    def _add_songs_without_albums(self, div, include_unknown_year, artist_url,
                                  albums):
        """TODO

        Parameters
        ----------
        div
        include_unknown_year
        artist_url
        albums

        """
        # The <div> tag refers to the section "other songs" which refers
        # to songs without album and year
        if include_unknown_year:
            logger.debug("<color>Processing the section 'other songs'...</color>")
            # Get all songs without album and year
            # Only get those songs (siblings) that are related
            # to the "other songs" section
            siblings = div.find_next_siblings()
            album_title = ""
            album_year = ""
            logger.debug("<color>{} items found for 'other songs'"
                         "</color>".format(len(siblings)))
            for index, sibling in enumerate(siblings, start=1):
                # logger.debug("<color>Processing sibling #{}"
                #              "</color>".format(index))
                if sibling.get('href'):
                    self._update_albums_dict(albums, sibling, album_title,
                                             album_year, artist_url)
                """
                else:
                    logger.debug("<color>Skipping sibling #{} since "
                                 "it's not a song</color>".format(
                                  index_other))
                """
            if albums.get(album_title):
                logger.debug("<color>{} songs added</color> from <color>"
                             "'other songs'</color>".format(
                              len(albums['']['songs'])))
        else:
            logger.debug("<color>No songs from the section 'other songs' will "
                         "be added</color>: they aren't part of albums nor do "
                         "they have a year")

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
        # TODO: explain
        assert which in ['song', 'album']
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

    @staticmethod
    def _check_album_year(year_result):
        """TODO

        Parameters
        ----------
        year_result : list
            TODO

        """
        # TODO: explain
        if len(year_result) != 1:
            raise lyrics_scraping.exceptions.NonUniqueAlbumYearError(
                "The album year extraction doesn't result in a UNIQUE number")
        elif not (len(year_result[0]) == 4 and
                  year_result[0].isdecimal()):
            raise lyrics_scraping.exceptions.WrongAlbumYearError(
                "The Album year extraction scheme broke: the year '{}' is not a "
                "number with four digits".format(year_result[0]))

    def _check_years(self, year_after, year_before):
        """TODO

        Parameters
        ----------
        year_after
        year_before

        Raises
        ------
        ValueError
            TODO

        """

        def _check_year(year, lower_limit, upper_limit):
            """TODO

            Parameters
            ----------
            year
            lower_limit
            upper_limit

            Returns
            -------
            TODO

            """
            return lower_limit <= year <= upper_limit

        # TODO: explain
        year_after = self.min_year if year_after is None else year_after
        current_year = int(time.strftime("%Y"))
        year_before = current_year if year_before is None else year_before
        years = namedtuple("years", "year_after year_before current_year year_min")
        years.year_after = year_after
        years.year_before = year_before
        years.current_year = current_year
        years.year_min = self.min_year
        for name in years._fields:
            year = years.__dict__[name]
            if not _check_year(year, self.min_year, current_year):
                error_msg = "{} should be a number with four digits and " \
                            "equal or less than {}".format(name, current_year)
                raise ValueError(error_msg)
        if year_before < year_after:
            error_msg = "year_before ({}) should be equal or greater than " \
                        "year_after {{}}".format(year_after, year_before)
            raise ValueError(error_msg)
        return years

    @staticmethod
    def _get_album_title_from_div_tag(div):
        """TODO

        Parameters
        ----------
        div

        Returns
        -------
        TODO

        """
        # Get the album's title from a <div> tag
        # Example:
        # <div class="album" id="7863">album: <b>"Speak &amp; Spell"
        # </b> (1981)</div>
        return div.contents[1].text.strip('"')

    def _get_albums_from_artist_webpage(self, soup, artist_url, include_unknown_year):
        """TODO

        Parameters
        ----------
        soup
        artist_url
        include_unknown_year

        Returns
        -------
        TODO

        """
        # Get all the <div> tags associated with albums
        # NOTE: even the section "other songs" is included even though it is for
        # songs without albums
        # Examples:
        # 1. <div class="album" id="7863">album: <b>"Speak &amp; Spell"</b>
        #    (1981)</div>
        # 2. <div class="album">other songs:</div>
        div_album_tags = soup.find_all("div", class_="album")
        # Process each <div> tag in order to extract useful info, e.g. album
        # title, its related songs, ...
        albums = {}
        logger.debug("<color>{} albums found</color>".format(
            len(div_album_tags)))
        for index_div, div in enumerate(div_album_tags, start=1):
            logger.debug("<color>Processing item #{}</color>".format(
                index_div))
            if div.text.count("other songs"):
                self._add_songs_without_albums(div, include_unknown_year,
                                               artist_url, albums)
            else:
                self._add_songs_from_same_album(div, artist_url, albums)
        return albums

    @staticmethod
    def _get_search_results(which, tags):
        """TODO

        Parameters
        ----------
        tags

        Returns
        -------

        """
        # TODO: explain
        assert which in ['album', 'artist', 'song']
        search_results_str = "\n"
        # NOTE: we start numbering at 1 instead of 0
        search_results_list = []
        for i, t in enumerate(tags, start=1):
            if which in ["album", "artist"]:
                # When album, text has the name of the artist followed by the
                # name of the album, e.g. Depeche Mode - Speak & Spell
                text = t.select_one("b").text
                search_results_list.append(text)
                search_results_str += "[{}] {}\n".format(i, text)
            else:  # song
                title, artist = t.select("b")
                title = title.text
                artist = artist.text
                search_results_list.append(title + " by " + artist)
                search_results_str += "[{}] {} by {}\n".format(i, title, artist)
        search_results = namedtuple("search_results",
                                    "search_results_str search_results_list")
        search_results.search_results_str = search_results_str
        search_results.search_results_list = search_results_list
        return search_results

    @staticmethod
    def _get_songs_urls_from_artist_webpage(soup):
        """TODO

        Parameters
        ----------
        soup

        Returns
        -------

        """
        # Get the list of songs URLs for the given artist
        # The URLs will be found as values to <a>'s href attributes
        # e.g. <a href="../lyrics/artist_name/song_title.html" ... >
        anchors = soup.find_all(href=re.compile("^../lyrics"))
        # Get only the songs URLs from the <a> tags
        return [a.attrs['href'] for a in anchors]

    def _multiple_search_result_case(self, msg, nb_results):
        """TODO

        Parameters
        ----------
        msg
        nb_results

        Returns
        -------

        """
        # TODO: explain
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

    def _select_best_match(self, word, possibilities):
        """TODO

        Parameters
        ----------
        word
        possibilities

        Returns
        -------

        """
        # TODO: explain
        # TODO: update following comment since we might also be using for albums
        # and artists
        # We choose the best song title and artist name from the
        # search results that match the user's given song title and
        # artist name
        matches = get_close_matches(word, possibilities)
        if matches:
            logger.debug(
                "<color>Found {} match{} for '{}':</color> {}".format(
                    len(matches),
                    plural(matches, "es"),
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

    def _single_search_result_case(self, msg):
        """TODO

        Parameters
        ----------
        msg

        Returns
        -------

        """
        # TODO: explain
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

    def _send_search_request(self, which, search_query):
        """TODO

        Parameters
        ----------
        which
        search_query

        Returns
        -------

        """
        # TODO: explain
        assert which in ['album', 'artist', 'song']
        self._search_url_params['q'] = search_query
        self._search_url_params['w'] = which + "s"
        logger.debug("<color>Sending {} search request ..."
                     "</color>".format(which))
        html = self.webcache.get_webpage(self.search_url,
                                         self._search_url_params)
        soup = BeautifulSoup(html, 'lxml')
        tags = soup.select("td.visitedlyr")
        return tags

    def _update_albums_dict(self, albums, anchor_tag, album_title, album_year,
                            artist_url):
        """TODO

        Parameters
        ----------
        albums : dict
        anchor_tag
        album_title
        album_year
        artist_url

        """
        song_title = anchor_tag.text
        """
        logger.debug("The song <color>'{}'</color> will be <color>"
                     "added</color>".format(song_title))
        """
        albums.setdefault(album_title, {})
        albums[album_title].setdefault('album_year', album_year)
        albums[album_title].setdefault('songs', [])
        song_url = self._complete_relative_url(anchor_tag['href'][2:], artist_url)
        song_data = (song_url, song_title)
        albums[album_title]['songs'].append(song_data)

    # TODO: change name to _get_songs
    def _get_lyrics(self, which, which_title=None, artist_name=None,
                    max_songs=None, year_after=None, year_before=None,
                    include_unknown_year=False, choose_random=False):
        """TODO

        Parameters
        ----------
        which
        which_title
        artist_name
        max_songs
        year_after
        year_before
        include_unknown_year
        choose_random

        Returns
        -------
        TODO

        """
        # TODO: explain
        # TODO: add assert msg and in other places too
        assert which in ['album', 'artist', 'song']
        if artist_name and which_title:
            query = "{} by {}".format(which_title, artist_name)
        elif which_title and not artist_name:
            query = which_title
            artist_name = ""
        else:
            query = artist_name
        tags = self._send_search_request(which, query)
        if not tags and artist_name:
            logger.debug("<color>Found 0 {} result</color>".format(which))
            logger.debug("<color>We will try to send the {} request with the "
                         "{} title only</color>".format(which, which))
            tags = self._send_search_request(which, which_title)
        if tags:
            logger.debug("<color>Found {} {} result{} (page 1)"
                         "</color>".format(len(tags), which, plural(tags)))
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
                logger.debug("<color>{} result{}: {}</color>".format(
                    which.upper(), plural(tags), search_results_str[:-1]))
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
                    logger.debug("<color>Choosing the first search result: "
                                 "{}</color>".format(search_results_list[0]))
                    tag = tags[0]
            url = tag.find("a").attrs['href']
            logger.debug("<color>{}'s URL: {}</color>".format(which, url))
            logger.debug("<color>Getting lyrics from the {}'s webpage ..."
                         "</color>".format(which))
            return self._get_lyrics_from_url(
                url,
                max_songs,
                year_after=year_after,
                year_before=year_before,
                include_unknown_year=include_unknown_year,
                choose_random=choose_random)
        else:  # tags is empty
            logger.warning(self.no_results_warning)
            return None

    # TODO: change name to _get_songs_from_url
    def _get_lyrics_from_url(self, url, max_songs=None, year_after=None,
                             year_before=None, include_unknown_year=False,
                             choose_random=False):
        """TODO

        Different scraping methods are called depending on the type of webpage:
        :meth:`._scrape_artist_page()` if it is an artist webpage and
        :meth:`_scrape_lyrics_page()` if it is a lyrics webpage.

        Parameters
        ----------
        url : str
            URL of the webpage to be scraped.
        max_songs
        year_after
        year_before
        include_unknown_year
        choose_random

        Returns
        -------
        TODO

        Raises
        ------
        InvalidURLCategoryError
            Raised if the URL is not recognized as referring to neither an
            artist nor a song webpage.

        See Also
        --------
        _scrape_artist_page : Scrapes an artist webpage.
        _scrape_lyrics_page : Scrapes a lyrics webpage.

        """
        # Check if the azlyrics URL belongs to a lyrics or artist
        # and start the scraping of the webpage
        if urlparse(url).path.startswith('/lyrics/'):
            # Lyrics URL
            logger.debug("<color>The URL refers to a lyrics webpage: {}"
                         "</color>".format(url))
            # TODO: raise error from _scrape_lyrics_page
            return self._scrape_lyrics_page(url)
        elif urlparse(url).path.startswith('/19/') or \
                urlparse(url).path[1].isalpha():
            # Artist URL
            # NOTE: artists' names that start with a number have their webpages
            # placed within the directory /19/
            # e.g. https://www.azlyrics.com/19/50cent.html
            logger.debug("<color>The URL {} refers to an artist webpage"
                         "</color>".format(url))
            # TODO: raise error from _scrape_artist_page
            return self._scrape_artist_page(
                url,
                max_songs,
                year_after=year_after,
                year_before=year_before,
                include_unknown_year=include_unknown_year,
                choose_random=choose_random)
        else:
            # Bad URL
            raise lyrics_scraping.exceptions.InvalidURLCategoryError(
                "The URL {} is not recognized as referring to either "
                "an artist or a lyrics webpage".format(url))

    # TODO: change name to _scrape_artist_webpage
    def _scrape_artist_page(self, artist_url, max_songs=None, year_after=None,
                            year_before=None, include_unknown_year=False,
                            choose_random=False):
        """Scrape the artist webpage.

        It crawls the artist webpage and scrapes any useful info to be saved,
        such as the artist's name, album title, and list of songs URLs.

        The artist webpage is cached so that we reduce the number of HTTP
        requests to the lyrics website.

        Parameters
        ----------
        artist_url : str
            URL to the artist webpage that is being scraped.
        max_songs
        year_after
        year_before
        include_unknown_year
        choose_random

        Raises
        ------
        TODO: remove these raises
        HTTP404Error
            Raised if the server returns a 404 status code because the webpage
            is not found. TODO: add link to custom exception
        requests.RequestException
            TODO

        See Also
        --------
        _scrape_lyrics_page : Scrapes a song webpage instead.

        """
        # TODO: explain
        years_data = self._check_years(year_after, year_before)
        # Check first if the URL was already processed, e.g. is found in the db
        # TODO: ...
        logger.debug("<color>Scraping the artist webpage {}</color>".format(
                     artist_url))
        ipdb.set_trace()
        artist_webpage = ArtistWebpage(artist_url, self.webcache,
                                       include_unknown_year, self.ignore_errors)
        # TODO: Save artist data
        albums = artist_webpage.get_albums()
        ipdb.set_trace()
        # Get the <div>'s id from the artist URL
        filter1 = AlbumIdFilter(album_id=artist_url.split("#")[1])
        filter2 = AlbumYearFilter(years_data)
        filter3 = MaxSongsFilter()
        albums.filter_songs([filter1, filter2, filter3])

        if ".html#" in artist_url:
            # Case where the artist URL points to a specific album within the
            # artist webpage
            #
            # NOTE: this happens when clicking on an album link from a search
            # result page after calling get_lyrics_from_album()
            #
            # Get the <div>'s id from the artist URL
            id_ = artist_url.split("#")[1]
            # Get the <div> tag associated with the id_
            # Example:
            # <div class="album" id="7863">album: <b>"Speak &amp; Spell"
            # </b> (1981)</div>
            div = soup.find("div", id=id_)
            # Get the album's title from the <div> tag
            album_title = self._get_album_title_from_div_tag(div)
            # Get songs from the given album
            songs = albums[album_title]['songs']
        elif year_after is None and year_before is None:
            # Case where the artist URL refers to all songs from the given
            # artist even those songs that are not associated to an album
            #
            # Get the list of songs URLs for the given artist
            songs = albums
        else:
            # Case where we must filter songs by years
            # NOTE: this happens when year_after and/or year_before are not None
            current_year = y.current_year
            if year_after == self.min_year and year_before == current_year:
                logger.debug("<color>No filtering based on year_after ({}) "
                             "and year_before ({})</color>".format(
                              year_after, year_before))
                songs = self._get_songs_urls_from_artist_webpage(soup)
            else:
                songs = []
                for album_title, data in albums.items():
                    album_year = data['album_year']
                    if not (year_before >= album_year >= year_after):
                        logger.debug("The album <color>'{}'</color> will be "
                                     "<color>rejected</color> because its year "
                                     "<color>{}</color> isn't not within <color>"
                                     "[{}, {}]</color>".format(
                                      album_title,
                                      album_year,
                                      year_after,
                                      year_before))
                    else:
                        songs.append(data)
        all_lyrics = []
        return all_lyrics

    # TODO: change name to _scrape_song_webpage
    def _scrape_lyrics_page(self, lyrics_url):
        """Scrape the lyrics webpage.

        It crawls the lyrics webpage and scrapes any useful info to be saved,
        such as the song title and the lyrics text.

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
            Raised if no album year or more than one album year were found
            on the lyrics webpage.
        WrongAlbumYearError
            Raised if the album year is not a number with four digits.

        See Also
        --------
        _scrape_artist_page : Scrapes an artist webpage instead.

        """
        # Check first if the URL was already processed, e.g. is found in the db
        if self._url_already_processed(lyrics_url) in [0, 2]:
            # Cache the webpage and retrieve its html content
            html = self.webcache.get_webpage(lyrics_url)
            logger.debug("Scraping the song webpage @ {}".format(lyrics_url))
            soup = BeautifulSoup(html, 'lxml')
            # Get the following data from the lyrics webpage:
            # - the title of the song
            # - the name of the artist
            # - the text of the song
            # - the album title
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
                len(album_result), plural(album_result)))
            if len(album_result) == 0:
                # No album found
                logger.debug("<color>No album found in the lyrics webpage: "
                             "{}</color>".format(lyrics_url))
                # Add empty string to the album result to notify that no album
                # was found when processing each album in the result
                album_result.append("")
            # Process each album from the album result
            for album in album_result:
                if album:
                    # The album title and year are found in a line like this:
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
                    # Sanity check on the album year: there should be only one
                    # album year extracted
                    if len(year_result) != 1:
                        # 0 or more than 1 album year found
                        raise lyrics_scraping.exceptions.NonUniqueAlbumYearError(
                            "The album year extraction doesn't result in a "
                            "UNIQUE number")
                    # Sanity check on the album year: the year should be a number
                    # with four digits
                    if not (len(year_result[0]) == 4 and
                            year_result[0].isdecimal()):
                        raise lyrics_scraping.exceptions.WrongAlbumYearError(
                            "The Album year extraction scheme broke: the year "
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


# TODO: add in utils
def complete_relative_url(relative_url, base_url):
    """TODO

    Parameters
    ----------
    relative_url
    base_url

    Returns
    -------
    TODO

    """
    parsed_url = urlparse(base_url)
    complete_url = '{}://{}{}'.format(parsed_url.scheme,
                                      parsed_url.hostname,
                                      relative_url)
    return complete_url


class SongsFilter:
    def __init__(self):
        pass

    def filter_albums(self, albums):
        raise NotImplementedError


class AlbumIdFilter(SongsFilter):
    def __init__(self, album_id):
        super().__init__()
        self.album_id = album_id

    def filter_albums(self, albums):
        """TODO

        Parameters
        ----------
        albums

        Returns
        -------
        TODO

        """
        if self.album_id:
            # Get only those songs associated with the given album_id
            return albums.get_songs_from_album_id(self.album_id)
        else:
            # No filtering based on the album_id=None
            return albums


class AlbumYearFilter(SongsFilter):
    def __init__(self, years):
        super().__init__()
        self.y = years

    def filter_albums(self, albums):
        """TODO

        Parameters
        ----------
        albums

        Returns
        -------
        TODO

        """
        # Case where we must filter albums by years
        # NOTE: this happens when year_after and/or year_before are not None
        year_before = self.y.year_before
        year_after = self.y.year_after
        if year_after == self.y.min_year and year_before == self.y.current_year:
            logger.debug("<color>No filtering based on year_after ({}) "
                         "and year_before ({})</color>".format(
                          year_after, year_before))
            return albums
        else:
            albums = {}
            for album_title, album_data in albums.items():
                album_year = album_data['album_year']
                if not (year_before >= album_year >= year_after):
                    logger.debug("The album <color>'{}'</color> will be "
                                 "<color>rejected</color> because its year "
                                 "<color>{}</color> isn't not within <color>"
                                 "[{}, {}]</color>".format(
                                  album_title,
                                  album_year,
                                  year_after,
                                  year_before))
                else:
                    albums.setdefault(album_title, album_data)
            return albums


class MaxSongsFilter(SongsFilter):
    def __init__(self):
        super().__init__()

    def filter_albums(self, albums):
        pass


class Albums:
    def __init__(self, artist_name, artist_url):
        self.artist_name = artist_name
        self.artist_url = artist_url
        self._albums = {}

    def filter_albums(self, filters):
        """TODO

        Parameters
        ----------
        filters : list of Filter

        Returns
        -------

        """
        albums = self._albums
        for f in filters:
            albums = f.filter_albums(albums)
        return albums

    # TODO: use property
    def get_albums(self):
        """TODO

        Returns
        -------
        TODO

        """
        return self._albums

    def get_songs_from_album_id(self, album_id):
        """TODO

        Parameters
        ----------
        album_id

        Returns
        -------
        TODO

        """
        for album_title, album_data in self._albums.items():
            if album_data['album_id'] == album_id:
                return self._albums[album_title]
        return None

    def get_songs_from_album_title(self, album_title):
        """TODO

        Parameters
        ----------
        album_title

        Returns
        -------
        TODO

        """
        return self._albums[album_title]['songs']

    def get_songs_from_year(self, year_after, year_before):
        pass

    def update_albums(self, anchor_tag, album_title, album_id, album_year):
        """TODO

        Parameters
        ----------
        anchor_tag
        album_title
        album_id
        album_year

        """
        song_title = anchor_tag.text
        """
        logger.debug("The song <color>'{}'</color> will be <color>"
                     "added</color>".format(song_title))
        """
        # TODO: album info should be done in a separate method
        self._albums.setdefault(album_title, {})
        self._albums[album_title].setdefault('album_id', album_id)
        self._albums[album_title].setdefault('album_year', album_year)
        self._albums[album_title].setdefault('songs', [])
        song_url = complete_relative_url(anchor_tag['href'][2:], self.artist_url)
        song_data = (song_url, song_title)
        self._albums[album_title]['songs'].append(song_data)


class ArtistWebpage:
    def __init__(self, artist_url, webcache, include_unknown_year, ignore_errors):
        self.artist_url = artist_url
        self.webcache = webcache
        self.include_unknown_year = include_unknown_year
        self.ignore_errors = ignore_errors
        # Retrieve the webpage's HTML
        # TODO: HTTP404Error and requests.RequestException are raised
        self.html = self.webcache.get_webpage(self.artist_url)
        self.soup = BeautifulSoup(self.html, 'lxml')
        # Get the name of the artist
        self.artist_name = self._scrape_artist_name()
        self.albums = Albums(self.artist_name, self.artist_url)
        self._scrape_albums()

    # TODO: use property
    def get_albums(self):
        """TODO

        Returns
        -------
        TODO

        """
        return self.albums.get_albums()

    # TODO: use property
    def get_artist_name(self):
        """TODO

        Returns
        -------
        TODO

        """
        return self.artist_name

    def _add_songs_from_same_album(self, div):
        """TODO

        Parameters
        ----------
        div

        Raises
        ------
        TODO

        """
        # TODO: explain
        # The <div> tag refers to an album
        # Get the album title
        album_title = self.scrape_album_title(div)
        # Get the album year
        year_result = re.findall(r'\((\d+)\)', div.text)
        # Sanity check the extracted album year
        try:
            Album.check_album_year(year_result)
        except (lyrics_scraping.exceptions.NonUniqueAlbumYearError,
                lyrics_scraping.exceptions.WrongAlbumYearError) as e:
            # TODO: add error in albums dict
            if self.ignore_errors:
                logger.error(e)
                logger.warning("<color>Skipping the album '{}'</color>".format(
                               album_title))
            else:
                raise e
        else:
            # Valid album year
            album_year = int(year_result[0])
            logger.debug("<color>The album '{}' ({}) will be added"
                         "</color>".format(album_title, album_year))
            # Get album's id
            album_id = self._scrape_album_id(div)
            # Get all songs from the given album
            # Only get those songs (siblings) that are related to the given album
            siblings = div.find_next_siblings()
            # TODO: [siblings_refactor]
            for index, sibling in enumerate(siblings, start=1):
                # A song must be associated with an <a href="..."> tag
                # Example:
                # <a href="../lyrics/depechemode/goingbackwards.html"
                # target="_blank"> Going Backwards</a>
                if sibling.get('href'):
                    self.albums.update_albums(sibling, album_title, album_id,
                                              album_year)
                elif sibling.get('class') and \
                        'album' in sibling.get('class'):
                    # We arrived at the beginning of another album. Thus, we must
                    # exit from the 'for loop' since we finished adding all songs
                    # from the given album
                    # Example:
                    # <div class="album" id="7852">album: <b>"A Broken Frame"
                    # </b> (1982)</div>
                    break
                else:
                    # Neither a song nor an album, e.g. <br/>
                    # Thus, we skip the current sibling
                    continue
            songs = self.albums.get_songs_from_album_title(album_title)
            if songs:
                logger.debug("<color>{} songs added from '{}'"
                             "</color>".format(len(songs), album_title))

    def _add_songs_without_albums(self, div):
        """TODO

        Parameters
        ----------
        div

        """
        # The <div> tag refers to the section "other songs" which corresponds
        # to songs without album and year
        if self.include_unknown_year:
            logger.debug("<color>Processing the section 'other songs'...</color>")
            # Get all songs without album and year
            # Only get those songs (siblings) that are related
            # to the "other songs" section
            siblings = div.find_next_siblings()
            album_title = ""
            album_id = ""
            album_year = ""
            logger.debug("<color>{} items found for 'other songs'"
                         "</color>".format(len(siblings)))
            for index, sibling in enumerate(siblings, start=1):
                # logger.debug("<color>Processing sibling #{}"
                #              "</color>".format(index))
                if sibling.get('href'):
                    self.albums.update_albums(sibling, album_title, album_id, album_year)
                """
                else:
                    logger.debug("<color>Skipping sibling #{} since "
                                 "it's not a song</color>".format(
                                  index_other))
                """
            songs = self.albums.get_songs_from_album_title(album_title)
            if songs:
                logger.debug("<color>{} songs added from 'other songs'"
                             "</color>".format(len(songs)))
        else:
            logger.debug("<color>No songs from the section 'other songs' will "
                         "be added</color>")

    def _scrape_albums(self):
        """TODO

        Returns
        -------
        TODO

        """
        # Get all the <div> tags associated with albums
        # NOTE: even the section "other songs" is included even though it is for
        # songs without albums
        # Examples:
        # 1. <div class="album" id="7863">album: <b>"Speak &amp; Spell"</b>
        #    (1981)</div>
        # 2. <div class="album">other songs:</div>
        div_album_tags = self.soup.find_all("div", class_="album")
        # Process each <div> tag in order to extract useful info, e.g. album
        # title, its related songs, ...
        logger.debug("<color>{} albums found</color>".format(
            len(div_album_tags)))
        for index_div, div in enumerate(div_album_tags, start=1):
            logger.debug("<color>Processing item #{}</color>".format(
                index_div))
            if div.text.count("other songs"):
                self._add_songs_without_albums(div)
            else:
                self._add_songs_from_same_album(div)
        ipdb.set_trace()

    @staticmethod
    def scrape_album_title(div):
        """TODO

        Parameters
        ----------
        div

        Returns
        -------
        TODO

        """
        # Get the album's title from a <div> tag
        # Example:
        # <div class="album" id="7863">album: <b>"Speak &amp; Spell"
        # </b> (1981)</div>
        return div.contents[1].text.strip('"')

    @staticmethod
    def _scrape_album_id(div):
        """TODO

        Parameters
        ----------
        div

        Returns
        -------
        TODO

        """
        # Get the album's id from a <div> tag
        # Example:
        # <div class="album" id="7863">album: <b>"Speak &amp; Spell"
        # </b> (1981)</div>
        return int(div.attrs['id'])

    def _scrape_artist_name(self):
        """TODO

        Returns
        -------
        TODO

        """
        # The name of the artist is found in the title of the artist webpage as
        # "ArtistName Lyrics"
        return self.soup.title.text.split(' Lyrics')[0]

    def _scrape_songs_urls(self):
        """TODO

        Parameters
        ----------
        soup

        Returns
        -------
        TODO

        """
        # Get the list of songs URLs for the given artist
        # The URLs will be found as values to <a>'s href attributes
        # e.g. <a href="../lyrics/artist_name/song_title.html" ... >
        anchors = self.soup.find_all(href=re.compile("^../lyrics"))
        # Get only the songs URLs from the <a> tags
        return [a.attrs['href'] for a in anchors]
