"""Imports:
    TrackData: for containing the extracted information
"""
import TrackData

def read_id3v2_tag_data(file_path):
    """Reads the ID3v2 tag data from a file (if present).

    ID3 v2.2.x, 2.3.x and 2.4.x tags are all supported.

    Args:
        file_path: String path to the file to read the tag from.

    Returns:
        A TrackData with the fields initialised to the data read from the tag.
        Non-present fields will be initialised to None. If no valid tag exists
        all fields will be None.
    """
    data = TrackData.TrackData()
    with open(file_path, "rb", 0) as f:
        header_data = f.read(10)

        # see what juicy goodies we have
        if header_data[:3] == "ID3":
            # check its not messed up
            assert_header_valid(header_data)
            # Parse the tag header. tag_size = total_tag_size - 10.
            tag_size = calculate_tag_size(header_data)
            total_tag_size = tag_size + 10

            # Read the frames
            total_read_size = 10
            while total_read_size < total_tag_size:
                # Parse the frame header. frame_size = total_frame_size - 10.
                f.seek(total_read_size, 0)
                frame_header_data = f.read(10)
                if frame_header_data[0] == '\00':
                    # If we have read a null byte we have reached the end of the
                    # ID3 tag. It turns out the majority of ID3 tags are heavily
                    # padded and are actually significantly longer than it needs
                    # to be so that editors can modify it without having to
                    # rewrite the entire MP3 file. This is poorly documented
                    # and, to me, really arcane - tags should not be frequently
                    # rewritten and being able to rewrite in-place seems a
                    # marginal optimisation at best. The ID3 tags I have tested
                    # are typically between 500 and 1000 bytes while actual
                    # allocation is around 4200 bytes per tag.
                    break
                frame_id = frame_header_data[0:4]
                frame_size = calculate_frame_size(frame_header_data)
                total_read_size += 10 + frame_size
                # Collect frame info
                if   frame_id == "TALB":
                    data.album = f.read(frame_size)[1:]
                elif frame_id == "TIT2":
                    data.title = f.read(frame_size)[1:]
                elif frame_id == "TPE1":
                    data.artist = f.read(frame_size)[1:]
                elif frame_id == "TRCK":
                    data.track = TrackData.mint(f.read(frame_size)[1:].split('/')[0])
                elif frame_id == "TYER":
                    data.year = TrackData.mint(f.read(frame_size)[1:5])
            # clean the strings generated
            data.clean(False) # TODO: This was previously True - correct?
    return data


def create_id3v2_tag_string(data, file_path):
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
        # check its not messed up
        assert_header_valid(track_data)
        # Parse the tag header. tag_size = total_tag_size - 10.
        tag_size = calculate_tag_size(track_data)
        total_tag_size = tag_size + 10
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
        total_read_size = 10
        while total_read_size < tag_size+10:
            if tag_data[total_read_size] == '\00':
                break
            frame_data = tag_data[total_read_size:total_read_size+10]
            frame_id = frame_data[0:4]
            frame_size = calculate_frame_size(frame_data)
            total_frame_size = frame_size + 10
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


def assert_header_valid(header):
    """Asserts an ID3v2 header is well formed

    Args:
        header: byte array constituting the tag header data to check.

    Returns:
        None

    Raises:
        Exception: if the header is invalid
    """
    # Check version: we only know at most about v2.4.0 (revisions are guaranteed
    # to be backwards compatible, but not 0xFF).
    version_okay = ord(header[3]) <= 0x04 and ord(header[4]) != 0xFF
    # Check flags: bit 6 (extended tag bit) may be legitimately set. Bit 7
    # (unsynchronised tag bit) is not currently supported. All other bits
    # represent non-standard extensions in v2.4 or earlier and assumed to render
    # the tag unreadable.
    flags_okay = (ord(header[5]) & ~0x40) == 0x00
    # Check size: size is encoded with MSB 0, all other sizes supported
    size_okay = ord(header[6]) < 0x80 and \
                ord(header[7]) < 0x80 and \
                ord(header[8]) < 0x80 and \
                ord(header[9]) < 0x80
    # Assert all is well
    header_okay = version_okay and flags_okay and size_okay
    if not header_okay:
        raise Exception("Attempting to create a new tag for a file with "
                        "corrupted ID3v2 tag. Exitting.")


def calculate_tag_size(header):
    """Calculates the size of an ID3v2.x tag

    The tag size (as returned) is defined as the complete ID3v2 tag size, minus
    the header (but not the extended header if one exists). Thus the returned
    tag_size = total_tag_size - 10.

    Args:
        header: byte array constituting the tag header data to check.

    Returns:
        The int tag_size of the tag
    """
    return (ord(header[6]) << 21) \
         + (ord(header[7]) << 14) \
         + (ord(header[8]) <<  7) \
         + (ord(header[9]))


def calculate_frame_size(frame):
    """Calculates the size of a tag frame

    The frame size (as returned) is defined as the complete size of the frame,
    minus the header. Thus the returned frame_size = total_frame_size - 10.

    Args:
        frame: byte array constituting the frame header data to check.

    Returns:
        The int frame_size of the frame
    """
    return (ord(frame[4]) << 24) \
         + (ord(frame[5]) << 16) \
         + (ord(frame[6]) <<  8) \
         + (ord(frame[7]))
