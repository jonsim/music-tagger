import re

class TrackData:
    title  = None
    album  = None
    artist = None
    track  = None
    year   = None
    genre  = None
    
    def __str__ (self):
        return "%02d %s - %s by %s in %d" % (self.track, self.title, self.album, self.artist, self.year)
    
    def clean(self, aggressive_cleaning=False):
        """ Cleans all string data on this TrackData.
        
        Args:
            aggressive_cleaning: Whether to pass this argument on to
                clean_string when using it to clean strings.
        
        Returns:
            None
        """
        self.title  = clean_string(self.title,  aggressive_cleaning) if self.title  else None
        self.album  = clean_string(self.album,  aggressive_cleaning) if self.album  else None
        self.artist = clean_string(self.artist, aggressive_cleaning) if self.artist else None


def mint(s):
    """ Converts a string to an int. null/empty string converted to None.

    Args:
        s: String to convert.

    Returns:
        Converted int, or None if the conversion was unsuccessful.
    """
    try:
        return int(s)
    except ValueError:
        return None


def clean_string(s, aggressive_cleaning=False):
    """ Cleans a string of weird punctuation or whitespace substitution.

    In detail the following cleaning will take place:
     * all but the last '.' are replaced with spaces
     * all '_' are replaced with spaces
     * all '-' are replaced with spaces
     * duplicate spaces are removed
     * capitalisation is converted to title case

    Args:
        aggressive_cleaning: Boolean flag. Set to True to perform additional,
            aggressive cleaning on the string to remove specific file name
            string mess.
    Returns:
        The cleaned up string.
    """
    # replace any of '.-_' with spaces (minus the last . for file extension).
    if s[-4:] == ".mp3":
        number_of_dots = s.count(".")
        s = s.replace('.', ' ', number_of_dots-1)
    else:
        s = s.replace('.', ' ')
    s = s.replace('-', ' ')
    s = s.replace('_', ' ')
    
    # lower the case.
    s = s.lower()
    
    # split the string into words (has the side effect of removing duplicate spaces).
    words = s.split()
    
    # fix the capitalisation.
    for i in range(len(words)):
        if i == 0 or (words[i] != "and" and words[i] != "at" and words[i] != "of" and words[i] != "or" and words[i] != "the"):
            words[i] = words[i][0].upper() + words[i][1:]
    
    # recombine the words into a string.
    s = " ".join(words)
    
    # specific additional cleaning methods for removing the detritus that commonly inhabits file
    # names. this should only be performed on filenames because it removes things like [...], which 
    # in the context of album folders frequently gives the publication year.
    if aggressive_cleaning:
        split = re.split("\[.*?\]", s)
        s = ' '.join(split)
        s = ' '.join(s.split())
    
    return s
