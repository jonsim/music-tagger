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
#import sys, string, os, re, operator
import sys, os, argparse
#from collections import defaultdict
import TrackCollection, TrackFile, TrackData
# This project makes use of the Levenshtein Python extension for string
# comparisons (edit distance and the like - used for fixing inconsistently
# named files). A copy of it is provided with this project, and the most
# recent version or more up to date information can be found at the 
# project page: http://code.google.com/p/pylevenshtein/
# To install, simply navigate to the python-Levenshtein-0.10.1 directory
# and run the command:
# python setup.py install
# NB: This requires that the 'python-dev' package is installed.




#-----------------------------------------------------------------------#
#--------------------    FILE HANDLING FUNCTIONS    --------------------#
#-----------------------------------------------------------------------#
def create_new_file(write_mode, music_file, output_file_path):
    if music_file.file_path == output_file_path and not write_mode:
        raise Exception("write_id3_v1_tag called and instructed to write over the file, however write mode (-f) is not enabled.")
    
    track_data = extract_track_data(music_file.file_path)
    id3v1_tag  = create_id3v1_tag(music_file)
    id3v2_tag  = create_id3v2_tag(music_file)
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

# Removes the words repeated in the same place in the strings in the list. This is necessary in the
# context of song filenames to undo filenames which include the artist or album name.
def remove_common_words (string_list):
    number_of_strings = len(string_list)
    
    # split each of the strings in the list into a list of words.
    word_list = []
    for i in range(number_of_strings):
        word_list.append(string_list[i].split())
    
    # calculate the number of words in the shortest string.
    len_shortest_string = len(word_list[0])
    for i in range(1, number_of_strings):
        if len(word_list[i]) < len_shortest_string:
            len_shortest_string = len(word_list[i])
    
    # for each of the possible shared words in the strings, check the words against the first word
    # for repetition, removing any that appear in the same place in every word (though only if the
    # run is at the start of the string (or 1 indented)).
    for i in range(len_shortest_string):
        exitted_early = 0
        for j in range(1, number_of_strings):
            if word_list[0][i] != word_list[j][i]:
                exitted_early = 1
                break
        if exitted_early == 0:
            for k in range(number_of_strings):
                word_list[k][i] = ""
        elif i > 0:
            break
    
    # recombine the word lists into a list of strings and return (removing additional spaces).
    return_list = []
    for i in range(number_of_strings):
        return_list.append(word_list[i][0])
        
        previous_blank = 0
        if (word_list[i][0] == ""):
            previous_blank = 1
        
        for j in range(1, len(word_list[i])):
            if previous_blank == 0:
                return_list[i] += " "
            return_list[i] += word_list[i][j]
            
            previous_blank = 0
            if word_list[i][j] == "":
                previous_blank = 1
    
    return return_list


# cleans all the files given to it (the cleaning only really makes sense per album folder).
def clean_folder (file_list):
    # create a cleaned copy of the file list
    cleaned_file_list = []
    for f in file_list:
        cleaned_file_list.append(TrackData.clean_string(f, True))
    # remove the common words
    if len(file_list) > 1:
        cleaned_file_list = remove_common_words(cleaned_file_list)
    return cleaned_file_list


# takes the supplied base folder file path and generates a filepath of a new folder in the directory
# below it
def generate_new_filepath (target_file_path):
    # get the absolute file path (use realpath rather than abspath to accomodate symlinks).
    abs_path = os.path.normpath(os.path.realpath(target_file_path))
    abs_path_split = os.path.split(abs_path)
    
    # check we can go down a level
    if abs_path_split[0] == '' or abs_path_split[1] == '':
        raise Exception("ERROR: You cannot ask the program to process the entire file system, please be more specific.")
    
    # generate the path of the next level down
    new_path = os.path.join(abs_path_split[0], 'music_tagger_output')
    if os.path.isdir(new_path):
        i = 1
        while os.path.isdir(new_path + str(i)):
            i += 1
        new_path += str(i)
    return new_path


def report_progress (string, percentage):
    if percentage == 100:
        sys.stdout.write("%s... %3d%%\n" % (string, percentage))
    else:
        sys.stdout.write("%s... %3d%%\r" % (string, percentage))
        sys.stdout.flush()




#-----------------------------------------------------------------------#
#---------------------------    MAIN CODE    ---------------------------#
#-----------------------------------------------------------------------#
def main():
    parser = argparse.ArgumentParser(description='A small program to tidy music '
        'files. It recursively explores a given directory and standardises '
        'folder structures, file naming conventions and ID3 tags.')
    parser.add_argument('directory', help='directory to recursively search for '
        'music files in')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    parser.add_argument('-f', '--write', action='store_true', help='write changes '
        'to disk. Default is to do a dry run (no file changes)')
    parser.add_argument('-d', '--directory-mode', action='store_true', help=
        'force the directory structure to be the ground truth, using its '
        'structure (artist/album/song.mp3) for the tag')
    args = parser.parse_args()
    # Parse command line arguments.
    if not args.directory_mode:
        print 'Error: directory mode (-d) is not enabled (i.e. you are telling\n' \
            'the program you have a mismatched folder structure), however the\n' \
            'functionality to deal with this scenario has not yet been\n' \
            'implemented. Sorry!'
        sys.exit()

    # create storage system
    music_collection = TrackCollection.TrackCollection()

    print "Indexing folder structure..."
    # Recursively tranverse from the provided root directory:
    #  * dirname gives the path to the current directory
    #  * dirnames gives the list of subdirectories in the folder
    #  * filenames gives the list of files in the folder
    # When mp3s are located, build internal data for each file.
    for dirname, subdirnames, filenames in os.walk(args.directory):
        cleaned_filenames = clean_folder(filenames)
        for i in range(len(filenames)):
            if filenames[i][-4:] == ".mp3":
                # Extract all the information possible from the song and add it.
                file_path = os.path.join(dirname, filenames[i])
                new_file = TrackFile.TrackFile(file_path, cleaned_filenames[i])
                new_file.load_all_data()
                new_file.finalise_data()
                music_collection.add(new_file)

    print "Processing indexed files."
    #report_progress("Processing indexed files", 0)
    music_collection.remove_duplicates()
    #report_progress("Processing indexed files", 50)
    music_collection.standardise_album_tracks()
    #report_progress("Processing indexed files", 100)

    if args.verbose:
        music_collection.sort_songs_by_track()
        print music_collection

    # write the newly corrected data to a new file system with new tags
    #new_folder = generate_new_filepath(args.directory)
    #print "Creating new directory structure in %s." % (new_folder)
    #music_collection.create_new_filesystem(new_folder)

    # done
    print "Finished."


# Entry point.
if __name__ == "__main__":
    main()
