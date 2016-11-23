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
    """
    title = None
    album = None
    artist = None
    track = None
    year = None

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

TITLE_CASE_EXCEPTIONS = ['a', 'at', 'by', 'in', 'of', 'or', 'to', 'and', 'the']

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
    # lower the case.
    string = string.lower()

    # if it's a filename, strip off the extension for later
    if string[-4:] == '.mp3':
        suffix = '.mp3'
        string = string[:-4]
    else:
        suffix = ''
    # replace any of '.-_' with spaces
    string = string.replace('.', ' ')
    string = string.replace('-', ' ')
    string = string.replace('_', ' ')

    # split the string into words and remove empty words (from duplicate spaces)
    words = [word for word in string.split() if word]

    # fix the capitalisation.
    words[0] = words[0].title()
    for i in range(1, len(words)):
        if words[i] not in TITLE_CASE_EXCEPTIONS:
            words[i] = words[i].title()

    # recombine the words into a string.
    string = ' '.join(words)

    # specific additional cleaning methods for removing the detritus that
    # commonly inhabits file names. this should only be performed on filenames
    # because it removes things like [...], which, in the context of album
    # folders frequently gives the publication year.
    if aggressive_cleaning:
        string = ' '.join(re.split(r'\[.*\]', string))

    return string + suffix
