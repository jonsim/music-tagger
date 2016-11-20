"""Imports:
    re: regexs for cleaning
"""
import re

class TrackData(object):
    """Generic information about a track.

    Attributes:
        title: string track title, None if not present
        album: string track album, None if not present
        artist: string track artist, None if not present
        track: int track number, None if not present
        year: int track year, None if not present
        genre: int track genre, None if not present
    """
    title = None
    album = None
    artist = None
    track = None
    year = None
    genre = None

    def __str__(self):
        """Override default str method """
        title_str = str(self.title)
        album_str = str(self.album)
        artist_str = str(self.artist)
        track_str = "%02d " % (self.track) if self.track else ""
        year_str = " in %d" % (self.year) if self.year else ""
        return "%s%s - %s by %s%s" % (track_str, title_str, album_str, artist_str, year_str)

    def __eq__(self, other):
        """Override default equality method """
        if isinstance(other, self.__class__):
            # Shorthand for saying all attributes must be equivalent
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Override default non-equality method """
        return not self.__eq__(other)

    def __hash__(self):
        """Override default hash behaviour """
        return hash(tuple(sorted(self.__dict__.items())))

    def clean(self, aggressive_cleaning=False):
        """Cleans all string data on this TrackData.

        Args:
            aggressive_cleaning: Whether to pass this argument on to
                clean_string when using it to clean strings.

        Returns:
            None
        """
        self.title = clean_string(self.title, aggressive_cleaning) if self.title else None
        self.album = clean_string(self.album, aggressive_cleaning) if self.album else None
        self.artist = clean_string(self.artist, aggressive_cleaning) if self.artist else None


def mint(string):
    """Converts a string to an int. null/empty string converted to None.

    Args:
        string: String to convert.

    Returns:
        Converted int, or None if the conversion was unsuccessful.
    """
    try:
        return int(string)
    except ValueError:
        return None


def clean_string(string, aggressive_cleaning=False):
    """Cleans a string of weird punctuation or whitespace substitution.

    In detail the following cleaning will take place:
     * all but the last '.' are replaced with spaces
     * all '_' are replaced with spaces
     * all '-' are replaced with spaces
     * duplicate spaces are removed
     * capitalisation is converted to title case

    Args:
        string: String to clean.
        aggressive_cleaning: Boolean flag. Set to True to perform additional,
            aggressive cleaning on the string to remove specific file name
            string mess.
    Returns:
        The cleaned up string.
    """
    # replace any of '.-_' with spaces (minus the last . for file extension).
    if string[-4:] == '.mp3':
        number_of_dots = string.count('.')
        string = string.replace('.', ' ', number_of_dots-1)
    else:
        string = string.replace('.', ' ')
    string = string.replace('-', ' ')
    string = string.replace('_', ' ')

    # lower the case.
    string = string.lower()

    # split the string into words (this will also remove duplicate spaces).
    words = string.split()

    # fix the capitalisation.
    title_case_exceptions = ['and', 'at', 'of', 'or', 'the']
    for i in range(len(words)):
        if (i == 0) or (words[i] not in title_case_exceptions):
            words[i] = words[i][0].upper() + words[i][1:]

    # recombine the words into a string.
    string = " ".join(words)

    # specific additional cleaning methods for removing the detritus that
    # commonly inhabits file names. this should only be performed on filenames
    # because it removes things like [...], which, in the context of album
    # folders frequently gives the publication year.
    if aggressive_cleaning:
        split = re.split(r'\[.*?\]', string)
        string = ' '.join(split)
        string = ' '.join(string.split())

    return string
