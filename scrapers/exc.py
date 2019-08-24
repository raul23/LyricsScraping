class InvalidURLCategoryError(Exception):
    """The URL is not recognized as belonging to neither of the valid
    categories"""


class InvalidURLDomainError(Exception):
    """The URL's domain is invalid"""


class MultipleAlbumError(Exception):
    """Album's info extraction scheme broke: more than one album were found"""


class MultipleLyricsURLError(Exception):
    """A lyrics URL was found more than once in the music db"""


class NonUniqueAlbumYearError(Exception):
    """Album's year extraction doesn't result in a UNIQUE number"""


class NonUniqueLyricsError(Exception):
    """Lyrics extraction scheme broke: no lyrics found or more than one lyrics
    were found"""


class OverwriteSongError(Exception):
    """A song was already found in the db and the db can't be updated"""


class WrongAlbumYearError(Exception):
    """Album's year is in the wrong century: only songs published in the 20th
    and 21th centuries are supported"""
