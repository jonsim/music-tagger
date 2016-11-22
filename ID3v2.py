"""Imports:
    TrackData: for containing the extracted information
"""
import TrackData

# Valid Frame IDs for each of the different versions
_V22_FRAME_IDS = [\
    "BUF", "CNT", "COM", "CRA", "CRM", "ETC", "EQU", "GEO", "IPL", "LNK", "MCI",
    "MLL", "PIC", "POP", "REV", "RVA", "SLT", "STC", "TAL", "TBP", "TCM", "TCO",
    "TCR", "TDA", "TDY", "TEN", "TFT", "TIM", "TKE", "TLA", "TLE", "TMT", "TOA",
    "TOF", "TOL", "TOR", "TOT", "TP1", "TP2", "TP3", "TP4", "TPA", "TPB", "TRC",
    "TRD", "TRK", "TSI", "TSS", "TT1", "TT2", "TT3", "TXT", "TXX", "TYE", "UFI",
    "ULT", "WAF", "WAR", "WAS", "WCM", "WCP", "WPB", "WXX"]
_V23_FRAME_IDS = [\
    "AENC", "APIC", "COMM", "COMR", "ENCR", "EQUA", "ETCO", "GEOB", "GRID",
    "IPLS", "LINK", "MCDI", "MLLT", "OWNE", "PRIV", "PCNT", "POPM", "POSS",
    "RBUF", "RVAD", "RVRB", "SYLT", "SYTC", "TALB", "TBPM", "TCOM", "TCON",
    "TCOP", "TDAT", "TDLY", "TENC", "TEXT", "TFLT", "TIME", "TIT1", "TIT2",
    "TIT3", "TKEY", "TLAN", "TLEN", "TMED", "TOAL", "TOFN", "TOLY", "TOPE",
    "TORY", "TOWN", "TPE1", "TPE2", "TPE3", "TPE4", "TPOS", "TPUB", "TRCK",
    "TRDA", "TRSN", "TRSO", "TSIZ", "TSRC", "TSSE", "TYER", "TXXX", "UFID",
    "USER", "USLT", "WCOM", "WCOP", "WOAF", "WOAR", "WOAS", "WORS", "WPAY",
    "WPUB", "WXXX"]
_V24_FRAME_IDS = _V23_FRAME_IDS + [\
    "ASPI", "EQU2", "RVA2", "SEEK", "SIGN", "TDEN", "TDOR", "TDRC", "TDRL",
    "TDTG", "TIPL", "TMCL", "TMOO", "TPRO", "TSOA", "TSOP", "TSOT", "TSST"]
_V22_V23_FRAME_ID_MAPPINGS = {\
    "BUF": "RBUF", "CNT": "PCNT", "COM": "COMM", "CRA": "AENC", "CRM": "ENCR",
    "ETC": "ETCO", "EQU": "EQUA", "GEO": "GEOB", "IPL": "IPLS", "LNK": "LINK",
    "MCI": "MCDI", "MLL": "MLLT", "PIC": "APIC", "POP": "POPM", "REV": "RVRB",
    "RVA": "RVAD", "SLT": "SYLT", "STC": "SYTC", "TAL": "TALB", "TBP": "TBPM",
    "TCM": "TCOM", "TCO": "TCON", "TCR": "TCOP", "TDA": "TDAT", "TDY": "TDLY",
    "TEN": "TENC", "TFT": "TFLT", "TIM": "TIME", "TKE": "TKEY", "TLA": "TLAN",
    "TLE": "TLEN", "TMT": "TMED", "TOA": "TOPE", "TOF": "TOFN", "TOL": "TOLY",
    "TOR": "TORY", "TOT": "TOAL", "TP1": "TPE1", "TP2": "TPE2", "TP3": "TPE3",
    "TP4": "TPE4", "TPA": "TPOS", "TPB": "TPUB", "TRC": "TSRC", "TRD": "TRDA",
    "TRK": "TRCK", "TSI": "TSIZ", "TSS": "TSSE", "TT1": "TIT1", "TT2": "TIT2",
    "TT3": "TIT3", "TXT": "TEXT", "TXX": "TXXX", "TYE": "TYER", "UFI": "UFID",
    "ULT": "USLT", "WAF": "WOAF", "WAR": "WOAR", "WAS": "WOAS", "WCM": "WCOM",
    "WCP": "WCOP", "WPB": "WPUB", "WXX": "WXXX"}
_V23_V22_FRAME_ID_MAPPINGS = {\
    "RBUF": "BUF", "PCNT": "CNT", "COMM": "COM", "AENC": "CRA", "ENCR": "CRM",
    "ETCO": "ETC", "EQUA": "EQU", "GEOB": "GEO", "IPLS": "IPL", "LINK": "LNK",
    "MCDI": "MCI", "MLLT": "MLL", "APIC": "PIC", "POPM": "POP", "RVRB": "REV",
    "RVAD": "RVA", "SYLT": "SLT", "SYTC": "STC", "TALB": "TAL", "TBPM": "TBP",
    "TCOM": "TCM", "TCON": "TCO", "TCOP": "TCR", "TDAT": "TDA", "TDLY": "TDY",
    "TENC": "TEN", "TFLT": "TFT", "TIME": "TIM", "TKEY": "TKE", "TLAN": "TLA",
    "TLEN": "TLE", "TMED": "TMT", "TOPE": "TOA", "TOFN": "TOF", "TOLY": "TOL",
    "TORY": "TOR", "TOAL": "TOT", "TPE1": "TP1", "TPE2": "TP2", "TPE3": "TP3",
    "TPE4": "TP4", "TPOS": "TPA", "TPUB": "TPB", "TSRC": "TRC", "TRDA": "TRD",
    "TRCK": "TRK", "TSIZ": "TSI", "TSSE": "TSS", "TIT1": "TT1", "TIT2": "TT2",
    "TIT3": "TT3", "TEXT": "TXT", "TXXX": "TXX", "TYER": "TYE", "UFID": "UFI",
    "USLT": "ULT", "WOAF": "WAF", "WOAR": "WAR", "WOAS": "WAS", "WCOM": "WCM",
    "WCOP": "WCP", "WPUB": "WPB", "WXXX": "WXX"}
_EXPERIMENTAL_FRAME_ID_PREFIXS = ["X", "Y", "Z"]


def _read_32bit_syncsafe(byte_data):
    """Reads a 32-bit syncsafe integer (28 bits with 4 sync bits zeroed out)

    Args:
        byte_data: character array of bytes. Must be 4 bytes long

    Returns:
        unsigned int representation of the byte data
    """
    int_bytes = [ord(b) for b in byte_data]
    if (int_bytes[0] & 0x80) or \
       (int_bytes[1] & 0x80) or \
       (int_bytes[2] & 0x80) or \
       (int_bytes[3] & 0x80):
        raise Exception("Attempt to read an invalid 32-bit syncsafe integer")
    return (int_bytes[0] << 21) \
         + (int_bytes[1] << 14) \
         + (int_bytes[2] <<  7) \
         + (int_bytes[3])


def _read_32bit_nonsyncsafe(byte_data):
    """Reads a standard 32-bit unsigned integer

    Args:
        byte_data: character array of bytes. Must be 4 bytes long

    Returns:
        unsigned int representation of the byte data
    """
    int_bytes = [ord(b) for b in byte_data]
    return (int_bytes[0] << 24) \
         + (int_bytes[1] << 16) \
         + (int_bytes[2] <<  8) \
         + (int_bytes[3])


def _read_24bit_nonsyncsafe(byte_data):
    """Reads a standard 24-bit unsigned integer

    Args:
        byte_data: character array of bytes. Must be 3 bytes long

    Returns:
        unsigned int representation of the byte data
    """
    int_bytes = [ord(b) for b in byte_data]
    return (int_bytes[0] << 16) \
         + (int_bytes[1] <<  8) \
         + (int_bytes[2])


def _read_16bit_nonsyncsafe(byte_data):
    """Reads a standard 16-bit unsigned integer

    Args:
        byte_data: character array of bytes. Must be 2 bytes long

    Returns:
        unsigned int representation of the byte data
    """
    int_bytes = [ord(b) for b in byte_data]
    return (int_bytes[0] <<  8) \
         + (int_bytes[1])


class _TagHeader(object):
    """ID3v2 tag header

    Attributes:
        version: int major version number (e.g. 4 for ID3v2.4.0)
        version_minor: int minor version number (e.g. 0 for ID3v2.4.0)
        header_size: int byte size of header data
        body_size: int byte size of all non-header data in the tag
        flags: dictionary mapping strings to bools for each available flag
        extended_header_size: int byte size of this version's extended header,
            if it has one. This attribute does not describe whether or not an
            extended header exists, only what size it would be if it did.
        frame_header_size: int byte size of this version's frame header size.
    """
    def __init__(self, header_data):
        """Interprets byte data as a tag header to build object

        Args:
            header_data: character array of bytes representing the tag header
        """
        # Check we're actually looking at an ID3v2 tag
        if header_data[:3] != "ID3":
            raise Exception("Given data does not contain an ID3v2 tag header")
        # Extract version number and assert it's supported
        self.version = ord(header_data[3])
        self.version_minor = ord(header_data[4])
        if self.version < 2 or self.version > 4 or self.version_minor == 0xFF:
            raise Exception("Unknown version 'ID3v2.%d.%d'" % (self.version, \
                self.version_minor))
        # Extract flags depending on version
        flag_int = ord(header_data[5])
        self.flags = {}
        if self.version == 2:
            self.extended_header_size = 0
            self.frame_header_size = 6
            self.flags['unsynchronisation'] = flag_int & 0x80
            self.flags['compression'] = flag_int & 0x40
            unknown_flags = flag_int & ~0xC0
        elif self.version == 3:
            self.extended_header_size = 10
            self.frame_header_size = 10
            self.flags['unsynchronisation'] = flag_int & 0x80
            self.flags['extended_header'] = flag_int & 0x40
            self.flags['experimental'] = flag_int & 0x20
            unknown_flags = flag_int & ~0xE0
        elif self.version == 4:
            self.extended_header_size = 6
            self.frame_header_size = 10
            self.flags['unsynchronisation'] = flag_int & 0x80
            self.flags['extended_header'] = flag_int & 0x40
            self.flags['experimental'] = flag_int & 0x20
            self.flags['footer_present'] = flag_int & 0x10
            unknown_flags = flag_int & ~0xF0
        # TODO: Handle unsupported flags
        # Ensure flags are valid
        if unknown_flags != 0:
            raise Exception("Unknown flags '0x%02X' (should be 0)" % (unknown_flags))
        # Extract size
        self.header_size = 10
        self.body_size = _read_32bit_syncsafe(header_data[6:10])
        # Assert frame size is valid
        if self.body_size == 0:
            raise Exception("Invalid Tag Size '0'")


    def __str__(self):
        """Override string printing method"""
        set_flags = [flag for flag in self.flags if self.flags[flag]]
        return "ID3v2.%d.%d Size=%d %s" % (self.version, self.version_minor,
                                           self.body_size, ','.join(set_flags))

    def has_extended_header(self):
        """Whether or not this the tag has an extended header

        Returns:
            bool, True if the tag has an extended header, False otherwise
        """
        if 'extended_header' in self.flags:
            return self.flags['extended_header'] != 0
        return False


class _TagExtendedHeader(object):
    """ID3v2 extended tag header

    Attributes:
        version: int version of the tag this extended header relates to
        header_size: int byte size of header data
        body_size: int byte size of all non-header data in this section
        flags: dictionary mapping strings to bools for each available flag
    """
    def __init__(self, version, xheader_data):
        """Interprets byte data as an extended tag header to build object

        Args:
            version: int version of the tag this frame was read from
            xheader_data: character array of bytes representing the extended tag
                header
        """
        self.flags = {}
        self.version = version
        if version == 3:
            self.header_size = 10
            self.body_size = _read_32bit_nonsyncsafe(xheader_data[0:4])
            flag_int = _read_16bit_nonsyncsafe(xheader_data[4:6])
            self.flags['crc_data_present'] = flag_int & 0x8000
            unknown_flags = flag_int & ~0x8000
        elif version == 4:
            self.header_size = 6
            self.body_size = _read_32bit_syncsafe(xheader_data[0:4]) - 6
            flag_int = ord(xheader_data[5])
            self.flags['tag_is_an_update'] = flag_int & 0x40
            self.flags['crc_data_present'] = flag_int & 0x20
            self.flags['tag_restrictions'] = flag_int & 0x10
            unknown_flags = flag_int & ~0x70
        else:
            raise Exception("Extended header on invalid version 'ID3v2.%d'" % (version))
        # TODO: Handle unsupported flags
        # Ensure flags are valid
        if unknown_flags != 0:
            raise Exception("Unknown flags '0x%02X' (should be 0)" % (unknown_flags))

    def __str__(self):
        """Override string printing method"""
        set_flags = [flag for flag in self.flags if self.flags[flag]]
        return "ExtendedHeader Size=%d %s" % (self.body_size, ','.join(set_flags))



class _FrameHeader(object):
    """ID3v2 tag frame

    Attributes:
        id: string id of the frame
        version: int version of the tag this frame was read from
        body_offset: the absolute file offset of this frame's body
        header_size: int byte size of header data
        body_size: int byte size of all non-header data in the frame
        flags: dictionary mapping strings to bools for each available flag
    """
    def __init__(self, version, header_data, offset):
        """Interprets byte data as a frame header to build object

        Args:
            version: int version of the tag this frame was read from
            header_data: character array of bytes representing the tag header
            offset: int absolute file offset of this frame's body
        """
        self.flags = {}
        self.version = version
        self.body_offset = offset
        # Extract header information depending on version
        if version == 2:
            self.id = header_data[:3]
            self.header_size = 6
            self.body_size = _read_24bit_nonsyncsafe(header_data[3:6])
            unknown_flags = 0
            valid_ids = _V22_FRAME_IDS
        elif version == 3:
            self.id = header_data[:4]
            self.header_size = 10
            self.body_size = _read_32bit_nonsyncsafe(header_data[4:8])
            flag_int = _read_16bit_nonsyncsafe(header_data[8:10])
            self.flags['tag_alter_preservation'] = flag_int & 0x8000
            self.flags['file_alter_preservation'] = flag_int & 0x4000
            self.flags['read_only'] = flag_int & 0x2000
            self.flags['compression'] = flag_int & 0x0080
            self.flags['encryption'] = flag_int & 0x0040
            self.flags['grouping_identity'] = flag_int & 0x0020
            unknown_flags = flag_int & ~0xE0E0
            valid_ids = _V23_FRAME_IDS
        elif version == 4:
            self.id = header_data[:4]
            self.header_size = 10
            self.body_size = _read_32bit_syncsafe(header_data[4:8])
            flag_int = _read_16bit_nonsyncsafe(header_data[8:10])
            self.flags['tag_alter_preservation'] = flag_int & 0x4000
            self.flags['file_alter_preservation'] = flag_int & 0x2000
            self.flags['read_only'] = flag_int & 0x1000
            self.flags['grouping_identity'] = flag_int & 0x0040
            self.flags['compression'] = flag_int & 0x0008
            self.flags['encryption'] = flag_int & 0x0004
            self.flags['unsynchronisation'] = flag_int & 0x0002
            self.flags['data_length_indicator'] = flag_int & 0x0001
            unknown_flags = flag_int & ~0x704F
            valid_ids = _V24_FRAME_IDS
        else:
            raise Exception("Unknown tag version 'ID3v2.%d'" % (version))
        # Assert frame id is known
        if not (self.id[0] in _EXPERIMENTAL_FRAME_ID_PREFIXS or self.id in valid_ids):
            if version == 3 and self.id[:3] in _V22_FRAME_IDS:
                # Some archaeic players (iTunes 6.0 in particular) write out
                # v2.3 tags but using v2.2 Frame IDs. Completely against the
                # standard but this affects enough files it's worth addressing...
                self.id = _V22_V23_FRAME_ID_MAPPINGS[self.id[:3]]
                # TODO: Warning?
            else:
                raise Exception("Unknown ID3v2.%d Frame ID '%s'" % (self.version, self.id))
        # Assert frame size is valid
        # TODO: Handle this properly
        if self.body_size == 0:
            #raise Exception("Invalid ID3v2.%d Frame Size '0'" % (self.version))
            print "WARNING: Empty frame found. Technically illegal"
        # TODO: Handle unsupported flags
        # Ensure flags are valid
        if unknown_flags != 0:
            raise Exception("Unknown ID3v2.%d Flags '0x%04X' (should be 0)" % \
                (self.version, unknown_flags))

    def __str__(self):
        """Override string printing method"""
        set_flags = [flag for flag in self.flags if self.flags[flag]]
        return "%s Size=%d %s" % (self.id, self.body_size, ','.join(set_flags))

    def read_body(self, file_handle):
        """Reads this frame's body content from the file

        Args:
            file_handle: file handle to read the data from. Must be opened at
                least as 'rb'.

        Returns:
            character byte array of data from the frame's body
        """
        file_handle.seek(self.body_offset, 0)
        return file_handle.read(self.body_size)


class _Tag(object):
    """ID3v2 tag

    Attributes:
        header: _TagHeader ID3v2 tag header
        extended_header: _TagExtendedHeader ID3v2 tag extended header, or None
        frames: list of _FrameHeader ID3v2 tag frame headers
    """
    def __init__(self, file_handle):
        """Reads an ID3v2 tag from a file. File must contain a tag.

        Args:
            file_handle: file handle open in at least 'rb' mode to read tag from
        """
        file_handle.seek(0, 0)
        # Read header
        header_data = file_handle.read(10)
        self.header = _TagHeader(header_data)
        total_size = self.header.header_size + self.header.body_size
        # Read extended header (if applicable)
        if self.header.has_extended_header():
            xheader_data = file_handle.read(self.header.extended_header_size)
            self.extended_header = _TagExtendedHeader(self.header.version, xheader_data)
            file_handle.seek(self.extended_header.body_size, 1)
        else:
            self.extended_header = None
        # Read frames
        self.frames = {}
        while file_handle.tell() < total_size:
            fheader_data = file_handle.read(self.header.frame_header_size)
            if fheader_data[0] == '\0':
                # If we have read a null byte we have reached the end of the
                # tag. It turns out the majority of ID3 tags are heavily padded
                # and are actually significantly longer than necessary so
                # editors can modify without having to rewrite the entire MP3
                # file. This is poorly documented.
                # The ID3 tags I have tested are typically between 500 and 1000
                # bytes while actual allocation is around 4200 bytes per tag.
                break
            frame = _FrameHeader(self.header.version, fheader_data, file_handle.tell())
            self.__add_frame(frame)
            file_handle.seek(frame.body_size, 1)

    def __str__(self):
        """Override string printing method"""
        frames_str = '\n  '.join([str(frame) for frame in self.frames])
        if self.extended_header:
            return "%s\n  %s\n  %s" % (str(self.header), str(self.extended_header), \
                                       frames_str)
        else:
            return "%s\n  %s" % (self.header, frames_str)

    def __add_frame(self, frame):
        """Adds the frame header to this tag

        Args:
            frame: _FrameHeader frame header to add

        Returns:
            None
        """
        self.frames[frame.id] = frame

    def __get_frame(self, frame_id):
        """Retrieves the frame header with the given ID

        Args:
            frame_id: ID of the frame header to retrieve

        Returns:
            _FrameHeader frame header
        """
        try:
            return self.frames[frame_id]
        except KeyError:
            return None

    def get_artist(self, file_handle):
        """Retrieves the track artist data from this tag

        Args:
            file_handle: open file handle to read the frame body from

        Returns:
            string track artist or None if this tag doesn't contain it
        """
        version = self.header.version
        if version == 2:
            frame_id = "TP1"
        elif version == 3 or version == 4:
            frame_id = "TPE1"
        else:
            return None
        frame = self.__get_frame(frame_id)
        if frame:
            return _read_frame_text(frame.read_body(file_handle))
        return None

    def get_album(self, file_handle):
        """Retrieves the track album data from this tag

        Args:
            file_handle: open file handle to read the frame body from

        Returns:
            string track album or None if this tag doesn't contain it
        """
        version = self.header.version
        if version == 2:
            frame_id = "TAL"
        elif version == 3 or version == 4:
            frame_id = "TALB"
        else:
            return None
        frame = self.__get_frame(frame_id)
        if frame:
            return _read_frame_text(frame.read_body(file_handle))
        return None

    def get_title(self, file_handle):
        """Retrieves the track title data from this tag

        Args:
            file_handle: open file handle to read the frame body from

        Returns:
            string track title or None if this tag doesn't contain it
        """
        version = self.header.version
        if version == 2:
            frame_id = "TT2"
        elif version == 3 or version == 4:
            frame_id = "TIT2"
        else:
            return None
        frame = self.__get_frame(frame_id)
        if frame:
            return _read_frame_text(frame.read_body(file_handle))
        return None

    def get_track(self, file_handle):
        """Retrieves the track number from this tag

        Args:
            file_handle: open file handle to read the frame body from

        Returns:
            int track number or None if this tag doesn't contain it
        """
        version = self.header.version
        if version == 2:
            frame_id = "TRK"
        elif version == 3 or version == 4:
            frame_id = "TRCK"
        else:
            return None
        frame = self.__get_frame(frame_id)
        if frame:
            body_data = _read_frame_text(frame.read_body(file_handle))
            return TrackData.mint(body_data.split('/')[0])
        return None

    def get_year(self, file_handle):
        """Retrieves the track year from this tag

        Args:
            file_handle: open file handle to read the frame body from

        Returns:
            int track year or None if this tag doesn't contain it
        """
        version = self.header.version
        if version == 2:
            frame_id = "TYE"
        elif version == 3 or version == 4:
            frame_id = "TYER"
        else:
            return None
        frame = self.__get_frame(frame_id)
        if frame:
            body_data = _read_frame_text(frame.read_body(file_handle))
            return TrackData.mint(body_data[0:4])
        return None

    def get_data(self, file_handle):
        """Extracts TrackData from this tag

        Args:
            file_handle: open file handle to read the relevant frames from

        Returns:
            TrackData with this tag's raw data
        """
        data = TrackData.TrackData()
        data.artist = self.get_artist(file_handle)
        data.album = self.get_album(file_handle)
        data.title = self.get_title(file_handle)
        data.track = self.get_track(file_handle)
        data.year = self.get_year(file_handle)
        return data


def _read_frame_text(body_data):
    """Parses a textual frame body as a python string

    Args:
        body_data: character array of bytes read from the frame body

    Returns:
        python string, decoded according to its character encoding
    """
    encoding = ord(body_data[0])
    # TODO: Deal with unicode properly (not using encode('ascii', 'replace'))
    if encoding == 0:   # ISO-8859-1
        return body_data[1:].decode('iso-8859-1').encode('ascii', 'replace')
    elif encoding == 1: # UTF-16
        return body_data[1:].decode('utf_16').encode('ascii', 'replace')
    elif encoding == 2: # UTF-16BE
        return body_data[1:].decode('utf_16_be').encode('ascii', 'replace')
    elif encoding == 3: # UTF-8
        return body_data[1:].decode('utf_8').encode('ascii', 'replace')
    return body_data


def calculate_tag_size(file_handle):
    """Calculates the size of an ID3v2.x tag

    Args:
        file_handle: a file handle opened in a readable binary mode

    Returns:
        int number of bytes in the tag, or 0 if the file does not have one
    """
    # Read the standard and extended tag headers
    cursor_pos = file_handle.tell()
    file_handle.seek(0, 0)
    tag_header = file_handle.read(10)
    file_handle.seek(cursor_pos, 0)
    # Calculate tag size
    if tag_header[:3] == "ID3":
        tag = _TagHeader(tag_header)
        return tag.header_size + tag.body_size
    return 0


def read_tag_data(file_path):
    """Reads the ID3v2 tag data from a file (if present).

    ID3 v2.2.x, 2.3.x and 2.4.x tags are all supported.

    Args:
        file_path: String path to the file to read the tag from.

    Returns:
        A TrackData with the fields initialised to the data read from the tag.
        Non-present fields will be initialised to None. If no valid tag exists
        None will be returned.
    """
    with open(file_path, "rb", 0) as f:
        has_tag = f.read(3) == "ID3"
        # If we don't have a tag, drop out
        if not has_tag:
            return None
        # Parse the tag
        tag = _Tag(f)
        data = tag.get_data(f)
        # clean the strings generated
        data.clean(False)
        return data
    return None


def create_tag_string(data, file_path):
    """Converts the given TrackData into a ID3v2.3.0 tag.

    Args:
        data: A TrackData object whose data will be put into the tag.
        file_path: A string file path to the MP3 file this TrackData is
            originally from. This is required as we read all other ID3v2 frames
            from it so we may preserve them. This is a bit of a hack.

    Returns:
        A string of the correct byte length representing the ID3v2.3.0 tag.
    """
    # FIXME: No need to take file_path and read file again. Should tag all
    # frames to the TrackData originally returned.
    def create_id3v2_frame_string(frame_id, frame_content):
        """Constructs an id3v2 text content frame.

        Args:
            frame_id: A string frame ID (four character identifier).
            frame_content: A string to place in the frame.

        Returns:
            A string representing this text frame
        """
        size = len(frame_content) + 2   # encoding mark + content + null byte
        size_b1 = (size >> 24) % 256
        size_b2 = (size >> 16) % 256
        size_b3 = (size >>  8) % 256
        size_b4 = size         % 256
        size_string = chr(size_b1) + chr(size_b2) + chr(size_b3) + chr(size_b4)
        flag_string = chr(0) + chr(0)
        frame = frame_id
        frame += size_string
        frame += flag_string
        frame += '\00'      # encoding mark (ISO-8859-1)
        frame += frame_content
        frame += '\00'
        return frame

    # read the entire input file in.
    with open(file_path, "rb") as f:
        track_data = f.read()

    # check what existing id3v2 tag we have (if any). if we have one, separate
    # the track from it.
    had_id3v2_tag = False
    if track_data[:3] == "ID3":
        had_id3v2_tag = True
        # Parse the tag header.
        tag = _TagHeader(track_data)
        total_tag_size = tag.header_size + tag.body_size
        tag_data = track_data[:total_tag_size]

    # create a new tag and add our data to it
    # write the frames to it (we do this before we write the header so we can
    # calculate the size)
    new_frames = create_id3v2_frame_string("TIT2", data.title)
    new_frames += create_id3v2_frame_string("TALB", data.album)
    new_frames += create_id3v2_frame_string("TPE1", data.artist)
    if data.track > 0:
        new_frames += create_id3v2_frame_string("TRCK", str(data.track))
    if data.year > 0:
        new_frames += create_id3v2_frame_string("TYER", str(data.year))
    # if we had an id3v2 tag before, copy the frames that we are not going to
    # replace over from it. This leaves frames we aren't updating unchanged - an
    # important consideration as some programs (i.e. windows media player) store
    # their own data in them and in some cases the frames will store user data
    # which will have taken some time to generate/collect, e.g. the POPM tag
    # (though this is far from a standard itself).
    if had_id3v2_tag:
        # TODO: This is going to screw up with id3v2.2 tags
        total_read_size = 10
        while total_read_size < total_tag_size:
            if tag_data[total_read_size] == '\00':
                break
            frame_data = tag_data[total_read_size:total_read_size+10]
            frame_id = frame_data[0:4]
            total_frame_size = _read_32bit_syncsafe(frame_data[4:8]) + 10
            # TODO: This if statement could be extended to include other frames
            # to be left out, or even replaced with just PRIV frames (UFID and
            # POPM should probably also be kept as they contain information
            # which will have been generated by other media players and is not
            # easily reproducible). For now I have chosen to err on the side of
            # caution and leave all other frames intact, but for a completely
            # clean and identically tagged music collection this is an option.
            if frame_id != "TALB" and \
               frame_id != "TIT2" and \
               frame_id != "TPE1" and \
               frame_id != "TRCK" and \
               frame_id != "TYER":
                new_frames += tag_data[total_read_size:total_read_size+total_frame_size]
            total_read_size += total_frame_size
    # calculate the size and add padding (I don't really like this approach, but
    # I guess there's a reason all the tracks I tested include large amounts of
    # padding so I will re-pad). Doing it at this stage leaves the option to
    # have the amount of padding added dependent on the tag size. For now simply
    # add 500 bytes of padding.
    new_frames += '\00' * 500
    size = len(new_frames)
    # produce the size string
    size_b1 = (size >> 21) % 128
    size_b2 = (size >> 14) % 128
    size_b3 = (size >>  7) % 128
    size_b4 = size         % 128
    size_string = chr(size_b1) + chr(size_b2) + chr(size_b3) + chr(size_b4)
    # write the header
    new_header = "ID3"                 # tag identifier
    new_header += chr(3) + chr(0)      # tag version number (v2.3.0)
    new_header += chr(0)               # flags
    new_header += size_string

    return new_header + new_frames
