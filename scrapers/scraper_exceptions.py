"""Module that defines exception related to web scraping of lyrics websites.

These are all the exceptions that are raised when running code from the
``scrapers`` package which defines the classes responsible for scraping
lyrics webpages.

"""


class InvalidURLCategoryError(Exception):
    """Raised if the URL is not recognized as belonging to none of the valid
    categories."""


class InvalidURLDomainError(Exception):
    """Raised if the URL's domain is invalid."""


class MultipleAlbumError(Exception):
    """Raised if the album's info extraction scheme broke: more than one album
    was found on the lyrics webpage."""


class MultipleLyricsURLError(Exception):
    """Raised if a lyrics URL was found more than once in the music db."""


class NonUniqueAlbumYearError(Exception):
    """Raised if the album's year extraction doesn't result in a UNIQUE number."""


class NonUniqueLyricsError(Exception):
    """Raised if the lyrics extraction scheme broke: no lyrics found or more
    than one lyrics were found on the lyrics webpage."""


class OverwriteSongError(Exception):
    """Raised if a song was already found in the db and the db can't be updated
    because updating the db is disabled by the user."""


class WrongAlbumYearError(Exception):
    """Raised if the album's year is in the wrong century: only songs
    published in the 20th and 21th centuries are supported."""
