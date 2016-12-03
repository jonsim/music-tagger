"""Imports:
    argparse: parsing command line arguments and providing help
    ConfigParser: parsing config files
"""
import sys
import argparse
import ConfigParser
from enum import Enum

CONFIG_FILE = 'music_tagger.ini'
INVALID_FILE_CHARS = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', "'"]

#
# CONFIG ENUMS
#

class ContinueBehaviour(Enum):
    """Enum representing ways to continue after dealing with unknown data."""
    ignore = 0  # Ignore event, continue execution
    stop = 1    # Halt execution on event
    parse = 2   # Attempt to process event

    @classmethod
    def from_string(cls, string, valid_values=None):
        """Derives a ContinueBehaviour from a string.

        Args:
            string: a string representation of the ContinueBehaviour.
            valid_values: optional list of valid string values it can take.

        Returns:
            ContinueBehaviour representation.

        Raises:
            Exception: if the string could not be parsed or was not valid.
        """
        if valid_values and string not in valid_values:
            raise Exception("ContinueBehaviour '%s' is not in valid values: "
                            "%s" % (string, str(valid_values)))
        if string in cls.__members__:
            return cls.__members__[string]
        raise Exception("Failed to parse ContinueBehaviour from '%s'" % (string))

class GenericState(Enum):
    """Enum representing a tri-state boolean with a wishy washy middle state."""
    no = 0
    maybe = 1
    yes = 2

    @classmethod
    def from_string(cls, string, no_val=None, maybe_val=None, yes_val=None):
        """Derives a GenericState from a string.

        Args:
            string: a string representation of the GenericState.
            no_val: optional string overriding the value of GenericState.no
            maybe_val: optional string overriding the value of GenericState.maybe
            yes_val: optional string overriding the value of GenericState.yes

        Returns:
            GenericState representation.

        Raises:
            Exception: if the string could not be parsed or was not valid.
        """
        if no_val and string == no_val:
            return cls.no
        if maybe_val and string == maybe_val:
            return cls.maybe
        if yes_val and string == yes_val:
            return cls.yes
        raise Exception("Failed to parse GenericState from '%s'" % (string))

class AlbumVariantStrategy(Enum):
    """Enum representing the strategy for dealing with album variants."""
    keep_both = 0
    keep_largest = 1
    merge = 2

    @classmethod
    def from_string(cls, string):
        """Derives a AlbumVariantStrategy from a string.

        Args:
            string: a string representation of the AlbumVariantStrategy.

        Returns:
            AlbumVariantStrategy representation.

        Raises:
            Exception: if the string could not be parsed or was not valid.
        """
        if string == 'keep-both':
            return cls.keep_both
        if string == 'keep-largest':
            return cls.keep_largest
        if string == 'merge':
            return cls.merge
        raise Exception("Failed to parse AlbumVariantStrategy from '%s'" % (string))

class AlbumYearStrategy(Enum):
    """Enum representing the strategy for dealing with differing album years."""
    majority = 0
    latest = 1
    ignore = 2

    @classmethod
    def from_string(cls, string):
        """Derives a AlbumYearStrategy from a string.

        Args:
            string: a string representation of the AlbumYearStrategy.

        Returns:
            AlbumYearStrategy representation.

        Raises:
            Exception: if the string could not be parsed or was not valid.
        """
        if string == 'majority':
            return cls.majority
        if string == 'latest':
            return cls.latest
        if string == 'ignore':
            return cls.ignore
        raise Exception("Failed to parse AlbumYearStrategy from '%s'" % (string))



def _int_from_string(string, valid_values=None):
    """Derives an int from a string.

    Args:
        string: a string representation of an int.
        valid_values: optional list of valid int values it can take.

    Returns:
        an int.

    Raises:
        Exception: if the string could not be parsed or was not valid.
    """
    try:
        i = int(string)
        if valid_values and i not in valid_values:
            raise Exception('int value invalid')
        return i
    except ValueError:
        raise Exception('int value invalid')

def _uint_from_string(string, str_mappings=None, valid_values=None):
    """Derives an int from a string.

    Args:
        string: a string representation of an unsigned int, or optionally a
            special string value.
        str_mappings: optional dict of string values to ints (positive or
            negative), allowed to parsed string.
        valid_values: optional list of valid int values it can take.

    Returns:
        an int.

    Raises:
        Exception: if the string could not be parsed or was not valid.
    """
    if str_mappings and string in str_mappings:
        return str_mappings[string]
    i = _int_from_string(string, valid_values=valid_values)
    if i < 0:
        raise Exception('int value invalid')
    return i

def _file_path_from_string(string):
    """Verifies a string is a valid file path (lacking invalid characters).

    Args:
        string: string to verify.

    Returns:
        The same string.

    Raises:
        Exception: if the string could not be parsed or was not valid.
    """
    if reduce(lambda x, y: x or y, [c in string for c in INVALID_FILE_CHARS]):
        raise Exception("File path '%s' contains at least one invalid character: "
                        "%s" % (string, ''.join(INVALID_FILE_CHARS)))
    return string

def _format_track_data(format_string, track_data):
    """Formats a naming pattern with data from a TrackData.

    Args:
        format_string: the naming pattern string to format.
        track_data: TrackData from which to take the substitution values.

    Returns:
        The formatted string.
    """
    format_string = format_string.replace('@A', track_data.artist)
    format_string = format_string.replace('@a', track_data.artist.lower())
    format_string = format_string.replace('@L', track_data.album)
    format_string = format_string.replace('@l', track_data.album.lower())
    format_string = format_string.replace('@N', track_data.title)
    format_string = format_string.replace('@n', track_data.title.lower())
    format_string = format_string.replace('@Y', ('%04d' % track_data.year)[-4:])
    format_string = format_string.replace('@y', ('%02d' % track_data.year)[-2:])
    format_string = format_string.replace('@T', ('%02d' % track_data.track))
    format_string = format_string.replace('@t', ('%d'   % track_data.track))
    return format_string

class Config(object):
    """Container for all program configuration and state.

    Attributes:
        directory: string directory to process (from command line).
        verbose: boolean whether or not to output verbose information.
        dry_run: boolean whether or not to do a dry run or an actual run.
        corrupted_frame_behaviour: ContinueBehaviour from corrupted-frames config.
        invalid_frame_behaviour: ContinueBehaviour from invalid-frames config.
        noncompliant_frame_behaviour: ContinueBehaviour from noncompliant-frames config.
        filename_space_char: string from filename-space-character config.
        string_format: string from string-format config.
        id3v1_version: int id3v1.X version number from id3v1-version config.
        id3v1_extension: boolean whether or not to output extended id3v1 tags.
        id3v2_version: int id3v2.X version number from id3v2-version config.
        embed_album_art: GenericState from embed-album-art config.
        remove_invalid_frames: GenericState from invalid-frames config.
        id3v2_padding: int number of bytes to pad with, or -1 for 'smart', from
            id3v2-padding config.
        renumber_cd_tracks: GenericState from renumber-cd-tracks config.
        album_variant_strategy: AlbumVariantStrategy from album-variant-strategy config.
        album_year_strategy: AlbumYearStrategy from album-year-strategy config.
    """
    def __init__(self):
        """Builds the program config from the command line and config file."""
        # Initialise command line argument parser
        self._argparser = argparse.ArgumentParser(description=\
            'A small program to tidy music files. It recursively explores a '
            'given directory and standardises folder structures, file naming '
            'conventions and ID3 tags.')
        self._argparser.add_argument('directory', help=\
            'directory to recursively search for music files in')
        self._argparser.add_argument('-v', '--verbose', action='store_true', help=\
            'verbose mode')
        self._argparser.add_argument('-f', '--write', action='store_true', help=\
            'write changes to disk. Default is to do a dry run (no file changes)')
        self._argparser.add_argument('-d', '--directory-mode', action='store_true', help=\
            'force the directory structure to be the ground truth, using its '
            'structure (artist/album/song.mp3) for the tag')
        # Initialise config file parser
        self._cfg = ConfigParser.RawConfigParser()

        # Parse command line arguments
        self._arg = self._argparser.parse_args()
        # Store parsed arguments
        self.directory = self._arg.directory
        self.verbose = True if self._arg.verbose else False
        self.dry_run = True if not self._arg.write else False
        if not self._arg.directory_mode:
            print 'Error: directory mode (-d) is not enabled (i.e. you are telling'
            print 'the program you have a mismatched folder structure), however the'
            print 'functionality to deal with this scenario has not yet been'
            print 'implemented. Sorry!'
            sys.exit()

        # Parse config file
        self._cfg.read(CONFIG_FILE)
        # Store parsed config
        self.corrupted_frame_behaviour = ContinueBehaviour.from_string(\
            self._cfg.get('input', 'corrupted-frames'), ['ignore', 'stop'])
        self.invalid_frame_behaviour = ContinueBehaviour.from_string(\
            self._cfg.get('input', 'invalid-frames'), ['ignore', 'stop'])
        self.noncompliant_frame_behaviour = ContinueBehaviour.from_string(\
            self._cfg.get('input', 'noncompliant-frames'))
        self._artist_name_format = _file_path_from_string(\
            self._cfg.get('output', 'artist-name-format'))
        self._album_name_format = _file_path_from_string(\
            self._cfg.get('output', 'album-name-format'))
        self._track_name_format = _file_path_from_string(\
            self._cfg.get('output', 'track-name-format'))
        self.filename_space_char = _file_path_from_string(\
            self._cfg.get('output', 'filename-space-character').replace("'", ""))
        self.string_format = \
            self._cfg.get('output', 'string-format')
        self.id3v1_version = _int_from_string(\
            self._cfg.get('output', 'id3v1-version')[0], [0, 1])
        self.id3v1_extension = \
            self._cfg.get('output', 'id3v1-version')[-1] == '+'
        self.id3v2_version = _int_from_string(\
            self._cfg.get('output', 'id3v2-version'), [2, 3, 4])
        self.embed_album_art = GenericState.from_string(\
            self._cfg.get('output', 'embed-album-art'), 'never', 'source', 'always')
        self.remove_invalid_frames = GenericState.from_string(\
            self._cfg.get('output', 'invalid-frames'), 'remove', None, 'retain')
        self.id3v2_padding = _uint_from_string(\
            self._cfg.get('output', 'id3v2-padding'), {'smart' : -1})
        self.renumber_cd_tracks = GenericState.from_string(\
            self._cfg.get('output', 'renumber-cd-tracks'), 'never', None, 'always')
        self.album_variant_strategy = AlbumVariantStrategy.from_string(\
            self._cfg.get('processing', 'album-variant-strategy'))
        self.album_year_strategy = AlbumYearStrategy.from_string(\
            self._cfg.get('processing', 'album-year-strategy'))

    def format_track_artist(self, track_data):
        """Returns the formatted track artist folder name.

        Formatting as defined by the artist-name-format config.

        Args:
            track_data: TrackData to input into the formatter.

        Returns:
            string formatted accordingly.
        """
        return _format_track_data(self._artist_name_format, track_data)

    def format_track_album(self, track_data):
        """Returns the formatted track album folder name.

        Formatting as defined by the album-name-format config.

        Args:
            track_data: TrackData to input into the formatter.

        Returns:
            string formatted accordingly.
        """
        return _format_track_data(self._album_name_format, track_data)

    def format_track_title(self, track_data):
        """Returns the formatted track file name.

        Formatting as defined by the track-name-format config.

        Args:
            track_data: TrackData to input into the formatter.

        Returns:
            string formatted accordingly.
        """
        return _format_track_data(self._track_name_format, track_data)
