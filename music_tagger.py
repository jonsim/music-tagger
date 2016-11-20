#!/usr/bin/python

#-----------------------------------------------------------------------#
#----------------------------    LICENSE    ----------------------------#
#-----------------------------------------------------------------------#
# This file is part of the music_tagger program                         #
# (https://github.com/jonsim/music_tagger).                             #
#                                                                       #
# music_tagger is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# music_tagger is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with music_tagger.  If not, see <http://www.gnu.org/licenses/>. #
#-----------------------------------------------------------------------#


#-----------------------------------------------------------------------#
#----------------------------     ABOUT     ----------------------------#
#-----------------------------------------------------------------------#
# A small program to tidy music files. It recursively explores a given  #
# directory and standardises folder structures, file naming conventions #
# and ID3 tags.                                                         #
# Author: Jonathan Simmonds                                             #
#-----------------------------------------------------------------------#


#-----------------------------------------------------------------------#
#----------------------------    IMPORTS    ----------------------------#
#-----------------------------------------------------------------------#
"""Imports:
    sys: console output
    os: walking the directory structure
    argparse: parsing command line arguments and providing help
    TrackData: storing data from a single source about a track
    TrackFile: collecting all a track's TrackData together
    TrackCollection: collecting all TrackFiles under in the searched directory
    Progress: formatting progress messages
"""
import sys
import os
import argparse
import TrackData
import TrackFile
import TrackCollection
import Progress
# This project makes use of the Levenshtein Python extension for string
# comparisons (edit distance and the like - used for fixing inconsistently
# named files). A copy of it is provided with this project, and the most
# recent version or more up to date information can be found at the
# project page: http://code.google.com/p/pylevenshtein/
# To install, simply navigate to the python-Levenshtein-0.10.1 directory
# and run the command:
# python setup.py install
# NB: This requires that the 'python-dev' package is installed.


# Progress reporting string constants.
SEARCHING_STATUS_STRING = '[1/5] Searching file structure'
INDEXING_STATUS_STRING = '[2/5] Indexing tracks'
PROCESSING_STATUS_STRING = '[3/5] Processing indexed tracks'
STANDARDISING_STATUS_STRING = '[4/5] Standardising track data'
REWRITING_STATUS_STRING = '[5/5] Rewriting tracks'


#-----------------------------------------------------------------------#
#--------------------    FILE HANDLING FUNCTIONS    --------------------#
#-----------------------------------------------------------------------#
def create_new_file(write_mode, music_file, output_file_path):
    if music_file.file_path == output_file_path and not write_mode:
        raise Exception("write_id3_v1_tag called and instructed to write over "
                        "the file, however write mode (-f) is not enabled.")
    track_data = extract_track_data(music_file.file_path)
    id3v1_tag = ID3v1.create_tag_string(music_file)
    id3v2_tag = create_id3v2_tag(music_file)
    with open(output_file_path, "wb") as f:
        f.write(id3v2_tag + track_data + id3v1_tag)


def extract_track_data(file_path):
    # read the entire input file in.
    with open(file_path, "rb") as f:
        track_data = f.read()

    # check if we have an id3v2 tag and strip it from the track data.
    if track_data[:3] == "ID3":
        # check its not messed up
        if ord(track_data[3]) == 0xFF or ord(track_data[4]) == 0xFF or ord(track_data[6]) >= 0x80 or ord(track_data[7]) >= 0x80 or ord(track_data[8]) >= 0x80 or ord(track_data[9]) >= 0x80:
            raise Exception("write_id3_v2_tag called on a file with a corrupted id3v2 tag. Exitting.")
        # Collect the tag header info. The tag_size is the complete ID3v2 tag size, minus the 
        # header (but not the extended header if one exists). Thus tag_size = total_tag_size - 10.
        tag_size = (ord(track_data[6]) << 21) + (ord(track_data[7]) << 14) + (ord(track_data[8]) << 7) + (ord(track_data[9]))
        track_data = track_data[tag_size+10:]

    # check if we have an id3v1 tag and strip it from the track data.
    if track_data[-128:-125] == "TAG":                      # check for v1.0/v1.1
        if track_data[-(128+227):-(128+227-4)] == "TAG+":   # check for v1.0 extended
            track_data = track_data[:-(128+227)]
        else:
            track_data = track_data[:-128]

    # return what's left
    return track_data



#-----------------------------------------------------------------------#
#-------------------    STRING HANDLING FUNCTIONS    -------------------#
#-----------------------------------------------------------------------#

class CleanFilename(object):
    """A tuple of cleaned filename and the original

    Attributes:
        original: string original filename
        cleaned: string post-processed filename"""
    def __init__(self, filename):
        self.original = filename
        self.cleaned = TrackData.clean_string(filename, True)


def remove_common_words(file_list):
    """ Removes words repeated in the same place in all strings in a list.

    This is necessary in the context of song filenames to undo filenames which
    include the artist or album name.

    Args:
        file_list: list of CleanFilename. The cleaned field will be used for
            comparison. The list is modified in place.

    Returns:
        A list of CleanFilenames with the common words removed.
    """

    # Split each of the strings in the list into a list of words.
    word_list = [(f.cleaned.split()) for f in file_list]

    # Calculate the number of words in the shortest string.
    len_shortest_string = len(min(word_list, key=len))

    # For each of the possible shared words in the strings, check against the
    # first word for repetition, removing any that appear in the same place in
    # every word (though only if the run is at the start of the string (or 1
    # indented)).
    file_count = len(file_list)
    for i in range(len_shortest_string):
        all_words_match = True
        for j in range(1, file_count):
            if word_list[0][i] != word_list[j][i]:
                all_words_match = False
                break
        if all_words_match:
            for k in range(file_count):
                word_list[k][i] = ""
        elif i > 0:
            break

    # Recombine the words for each file into a single name (removing additional
    # spaces) and overwrite the cleaned field.
    for i in range(file_count):
        file_list[i].cleaned = ' '.join([(w) for w in word_list[i] if w])

    return file_list


def clean_folder(file_list):
    """ Cleans all filenames given and removes common words from them.

    Args:
        file_list: list of strings representing filenames

    Returns:
        A list of CleanFilenames
    """
    if not file_list:
        return []
    cleaned_file_list = [(CleanFilename(f)) for f in file_list]
    return remove_common_words(cleaned_file_list)


# takes the supplied base folder file path and generates a filepath of a new folder in the directory
# below it
def generate_new_filepath(target_file_path):
    # get the absolute file path (use realpath rather than abspath to accomodate symlinks).
    abs_path = os.path.normpath(os.path.realpath(target_file_path))
    abs_path_split = os.path.split(abs_path)

    # check we can go down a level
    if abs_path_split[0] == '' or abs_path_split[1] == '':
        raise Exception("ERROR: You cannot ask the program to process the entire "
                        "file system, please be more specific.")

    # generate the path of the next level down
    new_path = os.path.join(abs_path_split[0], 'music_tagger_output')
    if os.path.isdir(new_path):
        i = 1
        while os.path.isdir(new_path + str(i)):
            i += 1
        new_path += str(i)
    return new_path


def print_warnings(warnings):
    """Outputs all warnings and clears the list

    Args:
        warnings: list of string warnings to print. This list will be cleared
            once printed.

    Returns:
        None
    """
    for warning in warnings:
        sys.stdout.write("WARNING: %s\n" % (warning))
    del warnings[:]


#-----------------------------------------------------------------------#
#---------------------------    MAIN CODE    ---------------------------#
#-----------------------------------------------------------------------#
def main():
    """Main function"""
    parser = argparse.ArgumentParser(description=\
        'A small program to tidy music files. It recursively explores a given '
        'directory and standardises folder structures, file naming conventions '
        'and ID3 tags.')
    parser.add_argument('directory', help=\
        'directory to recursively search for music files in')
    parser.add_argument('-v', '--verbose', action='store_true', help=\
        'verbose mode')
    parser.add_argument('-f', '--write', action='store_true', help=\
        'write changes to disk. Default is to do a dry run (no file changes)')
    parser.add_argument('-d', '--directory-mode', action='store_true', help=\
        'force the directory structure to be the ground truth, using its '
        'structure (artist/album/song.mp3) for the tag')
    args = parser.parse_args()
    # Parse command line arguments.
    if not args.directory_mode:
        print 'Error: directory mode (-d) is not enabled (i.e. you are telling\n' \
              'the program you have a mismatched folder structure), however the\n'\
              'functionality to deal with this scenario has not yet been\n' \
              'implemented. Sorry!'
        sys.exit()

    warnings = []

    # Recursively tranverse from the provided root directory looking for mp3s:
    #  * dirname gives the path to the current directory
    #  * dirnames gives the list of subdirectories in the folder
    #  * filenames gives the list of files in the folder
    Progress.state(SEARCHING_STATUS_STRING)
    track_list = []
    for dirname, subdirnames, filenames in os.walk(args.directory):
        cleaned_filenames = clean_folder(filenames)
        for f in cleaned_filenames:
            if f.original[-4:] == '.mp3':
                # Extract all the information possible from the song and add it.
                file_path = os.path.join(dirname, f.original)
                new_file = TrackFile.TrackFile(file_path, f.cleaned)
                track_list.append(new_file)
    track_count = len(track_list)

    # create storage system
    music_collection = TrackCollection.TrackCollection()

    # Add all located files to the collection.
    for i in range(track_count):
        track_list[i].load_all_data()
        track_list[i].finalise_data()
        music_collection.add(track_list[i])
        Progress.report(INDEXING_STATUS_STRING, track_count, i+1)
    print_warnings(warnings)

    # Remove all duplicate files from the collection.
    def progress_stub1(total_units, done_units):
        """Stub for encapsulating the 'processing'' formatter"""
        Progress.report(PROCESSING_STATUS_STRING, total_units, done_units)
    music_collection.remove_duplicates(warnings, progress_stub1)
    print_warnings(warnings)

    # Standardise track data on the remaining files.
    def progress_stub2(total_units, done_units):
        """Stub for encapsulating the 'standardising'' formatter"""
        Progress.report(STANDARDISING_STATUS_STRING, total_units, done_units)
    music_collection.standardise_album_tracks(warnings, progress_stub2)
    print_warnings(warnings)

    if args.verbose:
        music_collection.sort_songs_by_track()
        print music_collection

    if args.write:
        print "TBD"
        # write the newly corrected data to a new file system with new tags
        #new_folder = generate_new_filepath(args.directory)
        #print "Creating new directory structure in %s." % (new_folder)
        #music_collection.create_new_filesystem(new_folder)
    else:
        Progress.skip(REWRITING_STATUS_STRING)

    # done
    print "Finished."


# Entry point.
if __name__ == "__main__":
    main()
