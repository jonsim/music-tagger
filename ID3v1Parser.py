import TrackData


def strip_null_bytes(data):
    """ Strips extraneous whitespace and null bytes from data to give a string.

    Args:
        data: The raw string data to process.

    Returns:
        The stripped string.
    """
    return data.replace("\00", "").strip()


def pack_null_bytes (string, length):
    """ Packs a string into a given number of bytes and null terminates it.

    This is achieved either by truncating (when too long) or adding null bytes
    (when too short).

    Args:
        string: The string to pack. May be None.
        length: The number of bytes to pack to.

    Returns:
        A packed string of the requested number of bytes.
    """
    if string:
        if len(string) >= length-1:
            data = string[:length-1] + '\00'
        else:
            data = string + ('\00' * (length - len(string)))
    else:
        data = '\00' * length
    return data


def read_id3v1_tag_data(file_path):
    """Reads the ID3v1 tag data from a file (if present).

    ID3 v1.0 and v1.1 tags are supported along with extended tags.

    Args:
        file_path: String path to the file to read the tag from.

    Returns:
        A TrackData with the fields initialised to the data read from the tag.
        Non-present fields will be initialised to None. If no v1.0 or v1.1 tag
        exists all fields will be None.
    """
    data = TrackData.TrackData()
    with open(file_path, "rb", 0) as f:
        # Go to the (128+227)th byte before the end.
        f.seek(-(128+227), 2)
        # Read the 227 bytes that would make up the extended id3v1 tag.
        tagx_data = f.read(227)
        # Read the final 128 bytes that would make up the id3v1 tag.
        tag_data  = f.read(128)
        
        # See what juicy goodies we have.
        if tag_data[:3] == "TAG":
            # Either id3 v1.0 or v1.1
            data.title  = strip_null_bytes(tag_data[ 3:33])
            data.artist = strip_null_bytes(tag_data[33:63])
            data.album  = strip_null_bytes(tag_data[63:93])
            data.year   = None
            if tag_data[93:97] != "\00\00\00\00":
                data.year = TrackData.mint(strip_null_bytes(tag_data[93:97]))
            data.genre  = ord(tag_data[127])
            if ord(tag_data[125]) == 0 and ord(tag_data[126]) != 0:
                # id3 v1.1
                comment = strip_null_bytes(tag_data[97:125])
                data.track = ord(tag_data[126])
            else:
                # id3 v1.0
                comment = strip_null_bytes(tag_data[97:127])
            # check for extended tag and, if found, append to the data.
            if tagx_data[:4] == "TAG+":
                data.title  += strip_null_bytes(tagx_data[  4: 64])
                data.artist += strip_null_bytes(tagx_data[ 64:124])
                data.album  += strip_null_bytes(tagx_data[124:184])
            # clean the strings generated
            data.clean(False) # TODO: This was originally True - correct?
    return data


def create_id3v1_tag_string(data):
    """ Converts the given TrackData into a ID3v1.1 tag.

    Args:
        data: A TrackData object whose data will be put into the tag.

    Returns:
        A string of the correct byte length representing the ID3v1.1 tag.
    """
    if data.year:
        year_string = str(data.year)
    else:
        year_string = '\00' * 4
    # 3 B header, 30 B title, 30 B artist, 30 B album, 4 B year string,
    # 28 B comment, zero-byte (signifying v1.1), 1 B track, 1 B genre
    new_tag = "TAG" + pack_null_bytes(data.title,  30) \
                    + pack_null_bytes(data.artist, 30) \
                    + pack_null_bytes(data.album,  30) \
                    + year_string                      \
                    + '\00' * 28                       \
                    + '\00'                            \
                    + chr(data.track)                  \
                    + chr(data.genre)
    return new_tag

