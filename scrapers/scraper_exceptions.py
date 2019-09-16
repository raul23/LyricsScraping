"""Module that defines exceptions related to web scraping of lyrics websites.

These are all the exceptions that are raised when running code from the
``scrapers`` package [1] which defines the classes responsible for scraping
lyrics websites.

References
----------
.. [1] `scrapers package @ GitHub <https://bit.ly/2kkPjMP/>`_.

"""


class CurrentSessionDuplicateURLError(Exception):
    """Raised if the URL was already processed during the current session."""


class InvalidURLCategoryError(Exception):
    """Raised if the URL is not recognized as belonging to none of the valid
    categories."""


class InvalidURLDomainError(Exception):
    """Raised if the URL's domain is invalid."""


class MultipleAlbumError(Exception):
    """Raised if the album extraction scheme broke: more than one album was
    found on the lyrics webpage."""


class MultipleLyricsURLError(Exception):
    """Raised if a lyrics URL was found more than once in the music db."""


class NonUniqueAlbumYearError(Exception):
    """Raised if the album's year extraction scheme broke: no year found or
    more than one year were found on the lyrics webpage."""


class NonUniqueLyricsError(Exception):
    """Raised if the lyrics extraction scheme broke: no lyrics found or more
    than one lyrics were found on the lyrics webpage."""


class OverwriteSongError(Exception):
    """Raised if a song was already found in the db and the db can't be updated
    because it is disabled by the user."""


class WrongAlbumYearError(Exception):
    """Raised if the album's year extraction scheme broke: the album's year is
    not a number with four digits."""
