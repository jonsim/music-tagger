"""Imports:
    re: regexes for extracting data
    TrackData: for containing the extracted information"""
import re
import TrackData

def read_file_path_data(file_path, cleaned_filename):
    """ Parses TrackData from a file path.

    The file path provides the majority of the information though a
    cleaned_filename needs to be passed in (which is designed to be one of the
    outputs from clean_folder()) as this method will have access to only the
    single file, not the entire folder of files which is necessary for the full
    cleaning (e.g. removing repeated words).

    Args:
        file_path: String path to the file to generate data for.
        cleaned_filename: The file name, cleaned to remove unusual formatting.

    Returns:
        A TrackData with the fields initialised to the parsed data. Unparsable
        fields will be initialised to None.
    """
    data = TrackData.TrackData()
    # Attempt to collect information from the file's path (the album / artist).
    file_path_split = file_path.split(r'/')
    # If correctly set up: -1 holds the file name; -2 the album folder; -3 the
    # artist folder.
    if len(file_path_split) >= 3:
        candidate_album_name = TrackData.clean_string(file_path_split[-2])
        if re.match(r'\[\d\d\d\d\] ', candidate_album_name) != None:
            data.album = candidate_album_name[7:]
            data.year = int(candidate_album_name[1:5])
        else:
            data.album = candidate_album_name
        data.artist = TrackData.clean_string(file_path_split[-3])

    # Attempt to collect information from the file's name (the track number / name).
    filename_split = cleaned_filename.split()
    if filename_split[0].isdigit():
        data.track = int(filename_split[0])
        data.title = ' '.join(filename_split[1:]).split('.')[0]
    else:
        data.title = ' '.join(filename_split).split('.')[0]
    return data
