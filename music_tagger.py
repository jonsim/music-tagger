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
import sys, string, os, re
# This project makes use of the Levenshtein Python extension for the string comparisons (edit 
# distance and the like). A copy of it is provided with this project, and the most recent version 
# or more up to date information can be found at the project page: http://code.google.com/p/pylevenshtein/
# To install, simply navigate to the python-Levenshtein-0.10.1 directory and run the command:
# python setup.py install
import Levenshtein
# for multi-dimensional dictionaries
from collections import defaultdict




#-----------------------------------------------------------------------#
#------------------------    CLASS DEFINITIONS    ----------------------#
#-----------------------------------------------------------------------#
class MusicFile:
    # File path, the only required and certain piece of data.
    file_path = ""
    #fp_data_loaded = False
    #v1_data_loaded = False
    #v2_data_loaded = False
    final_data_set = False
    # Data extracted from the file path.
    fp_title  = ""
    fp_album  = ""
    fp_artist = ""
    fp_track  = 0
    fp_year   = 0
    # Data extracted from the ID3v1 tag.
    v1_title  = ""
    v1_album  = ""
    v1_artist = ""
    v1_track  = 0
    v1_year   = 0
    v1_genre  = 0
    # Data extracted from the ID3v2 tag.
    v2_title  = ""
    v2_album  = ""
    v2_artist = ""
    v2_track  = 0
    v2_year   = 0
    v2_genre  = 0
    # Final data.
    final_title = ""
    final_album = ""
    final_artist = ""
    final_track = 0
    final_year = 0
    final_genre = 0
    
    
    # Note that not giving it a cleaned filename will cause one to be generated automatically for
    # you. The downside of this is that it will be treated in isolation to all other files in the 
    # directory so it cannot perform common word removal or anything clever.
    def __init__ (self, file_path, cleaned_filename=""):
#        print "Creating a MusicFile (%s)." % file_path
        if file_path == "":
            raise Exception("Cannot create a MusicFile with an empty file_path.")
        self.file_path = file_path
        if cleaned_filename == "":
            self.cleaned_filename = clean_string(file_path.split('/')[-1])
        else:
            self.cleaned_filename = cleaned_filename
    
    
    def __str__ (self):
        if self.final_data_set:
            s = "MusicFile compressed data:\n"
            s += "  %d %s - %s by %s on %d" % (self.final_track, self.final_title, self.final_album, self.final_artist, self.final_year)
        else:
            s = "MusicFile uncompressed data:\n"
            s += "  fp) %d %s - %s by %s on %d\n" % (self.fp_track, self.fp_title, self.fp_album, self.fp_artist, self.fp_year)
            s += "  v1) %d %s - %s by %s on %d\n" % (self.v1_track, self.v1_title, self.v1_album, self.v1_artist, self.v1_year)
            s += "  v2) %d %s - %s by %s on %d"   % (self.v2_track, self.v2_title, self.v2_album, self.v2_artist, self.v2_year)
        return s
    
    
    # Compresses the data from all the loaded sources together into the final data set.
    def compress_all_data (self):
        def compress_string_data (fp=None, v1=None, v2=None):
            # We tend to favour fp while v1 and v2 have equal weighting. We assume v1 could have
            # been truncated to 30 characters (hence why, when it is compared with other strings 
            # they have to be cut down and it is never directly returned).
            fp_v1_distance = 0
            fp_v2_distance = 0
            v1_v2_distance = 0
            DISTANCE_THRESHOLD = 3
            # title
            if fp and v1:
                fp_v1_distance = Levenshtein.distance(fp[:30], v1)
            if fp and v2:
                fp_v2_distance = Levenshtein.distance(fp,      v2)
            if v1 and v2:
                v1_v2_distance = Levenshtein.distance(v1,      v2[:30])
            
            # If fp is similar to one of them, return fp. Otherwise if v1 and v2 are similar, return
            # v2. Otherwise just return fp (as good as random chance, maybe print something).
            if (fp and v1 and fp_v1_distance < DISTANCE_THRESHOLD) or (fp and v2 and fp_v2_distance < DISTANCE_THRESHOLD):
                return fp
            elif v1 and v2 and v1_v2_distance < DISTANCE_THRESHOLD:
                return v2
            elif fp:
                return fp
            elif v2:
                return v2
            elif v1:
                return v1
            else:
                # As all string data is essential, raise an exception if a load is missing.
                raise Exception("compress_string_data called with no arguments.")
        
        def compress_integer_data (fp=None, v1=None, v2=None):
            if (fp and v1 and fp == v1) or (fp and v2 and fp == v2):
                return fp
            elif v1 and v2 and v1 == v2:
                return v2
            elif fp:
                return fp
            elif v2:
                return v2
            elif v1:
                return v1
            # As all integer data is non-essential don't bother even mentioning it.
            else:
                print "Warning: compress_integer_data called with no arguments."
        
        self.final_title  = compress_string_data( self.fp_title,  self.v1_title,  self.v2_title)
        self.final_album  = compress_string_data( self.fp_album,  self.v1_album,  self.v2_album)
        self.final_artist = compress_string_data( self.fp_artist, self.v1_artist, self.v2_artist)
        self.final_track  = compress_integer_data(self.fp_track,  self.v1_track,  self.v2_track)
        self.final_year   = compress_integer_data(self.fp_year,   self.v1_year,   self.v2_year)
        self.final_genre  = compress_integer_data(None,           self.v1_genre,  self.v2_genre)
        self.final_data_set = True
    
    
    # Loads all the data possible. Simply a convenience method.
    def load_all_data (self):
        self.load_file_path_info()
        self.load_id3v1_tag()
        self.load_id3v2_tag()
    
    
    # Loads the object with all the song data. The file path provides the majority of the information
    # though a cleaned_filename needs to be passed in (which is designed to be one of the outputs
    # from clean_folder()) as this method will have access to only the single file, not the entire
    # folder of files which is necessary for the full cleaning (e.g. removing repeated words).
    def load_file_path_info (self):
        # Attemtpt to collect information from the file's path (the album / artist).
        file_path_split = self.file_path.split('/')
        # If correctly set up: -1 holds the file name; -2 the album folder; -3 the artist folder.
        if len(file_path_split) >= 3:
            candidate_album_name = clean_string(file_path_split[-2])
            if re.match('\[\d\d\d\d\] ', candidate_album_name) != None:
                self.fp_album = candidate_album_name[7:]
                self.fp_year = int(candidate_album_name[1:5])
            else:
                self.fp_album = candidate_album_name
            self.fp_artist = clean_string(file_path_split[-3])
        
        # Attempt to collect information from the file's name (the track number / name).
        filename_split = self.cleaned_filename.split()
        if filename_split[0].isdigit():
            self.fp_track = int(filename_split[0])
            self.fp_title = ' '.join(filename_split[1:]).split('.')[0]
        else:
            self.fp_title = ' '.join(filename_split).split('.')[0]
        #self.fp_data_loaded = True
    
    
    # Reads the ID3v1 tag data from a file (if present). ID3 v1.0 and v1.1 tags are supported along with extended tags.
    def load_id3v1_tag (self):
        with open(self.file_path, "rb", 0) as f:
            f.seek(-(128+227), 2)    # go to the (128+227)th byte before the end
            tagx_data = f.read(227)  # read the 227 bytes that would make up the extended id3v1 tag.
            tag_data  = f.read(128)  # read the final 128 bytes that would make up the id3v1 tag.
            
            # see what juicy goodies we have.
            if tag_data[:3] == "TAG":
                # either id3 v1.0 or v1.1
                self.v1_title  = strip_null_bytes(tag_data[ 3:33])
                self.v1_artist = strip_null_bytes(tag_data[33:63])
                self.v1_album  = strip_null_bytes(tag_data[63:93])
                self.v1_year = 0
                if tag_data[93:97] != "\00\00\00\00":
                    self.v1_year = int(strip_null_bytes(tag_data[93:97]))
                self.v1_genre  = ord(tag_data[127])
                if ord(tag_data[125]) == 0 and ord(tag_data[126]) != 0:
                    # id3 v1.1
                    comment = strip_null_bytes(tag_data[97:125])
                    self.v1_track = ord(tag_data[126])
#                    print "ID3v1.1   tag found: '%s' - '%s' by '%s' in %d, track %d, genre %d" % (self.v1_title, self.v1_album, self.v1_artist, self.v1_year, self.v1_track, self.v1_genre)
                else:
                    # id3 v1.0
                    comment = strip_null_bytes(tag_data[97:127])
#                    print "ID3v1.0   tag found: '%s' - '%s' by '%s' in %d, genre %d" % (self.v1_title, self.v1_album, self.v1_artist, self.v1_year, self.v1_genre)
                # check for extended tag and, if found, add its stuff to the data.
                if tagx_data[:4] == "TAG+":
                    self.v1_title  += strip_null_bytes(tagx_data[  4: 64])
                    self.v1_artist += strip_null_bytes(tagx_data[ 64:124])
                    self.v1_album  += strip_null_bytes(tagx_data[124:184])
                # clean the strings generated
                self.v1_title  = clean_string(self.v1_title)
                self.v1_artist = clean_string(self.v1_artist)
                self.v1_album  = clean_string(self.v1_album)
            else:
                print "No ID3v1 tag found."
                #self.v1_data_loaded = False
    
    
    # Reads the ID3v2 tag data from a file (if present).
    def load_id3v2_tag (self):
        with open(self.file_path, "rb", 0) as f:
            header_data = f.read(10)
            
            # see what juicy goodies we have
            if header_data[:3] == "ID3":
                # check its not messed up
                if ord(header_data[3]) == 0xFF or ord(header_data[4]) == 0xFF or ord(header_data[6]) >= 0x80 or ord(header_data[7]) >= 0x80 or ord(header_data[8]) >= 0x80 or ord(header_data[9]) >= 0x80:
                    print "corrupted tag found, exitting."
                    return
                # Collect the tag header info. The tag_size is the complete ID3v2 tag size, minus the 
                # header (but not the extended header if one exists). Thus tag_size = total_tag_size - 10.
                tag_size = (ord(header_data[6]) << 21) + (ord(header_data[7]) << 14) + (ord(header_data[8]) << 7) + (ord(header_data[9]))
                #print "found ID3v2.%d.%d tag (size %d bytes)" % (ord(header_data[3]), ord(header_data[4]), tag_size)
                version_string = "ID3v2.%d.%d" % (ord(header_data[3]), ord(header_data[4]))
                
                # Read the frames
                total_read_size = 10
                while (total_read_size < tag_size+10):
                    # Collect the frame header info. the frame_size is the size of the frame, minus the
                    # header. Thus frame_size = total_frame_size - 10.
                    f.seek(total_read_size, 0)
                    frame_header_data = f.read(10)
                    if frame_header_data[0] == '\00':
                        # If we have read a null byte we have reached the end of the ID3 tag. It turns 
                        # out the majority of ID3 tags are heavily padded and are actually significantly 
                        # longer than it needs to be so that editors can modify it without having to 
                        # rewrite the entire MP3 file. This is poorly documented and, to me, really 
                        # arcane - I can't see why you would want to avoid having to rewrite the whole 
                        # file. The ID3 tags I have tested are typically between 500 and 1000 bytes 
                        # while around 4200 bytes is actually allocated.
                        break
                    frame_id = frame_header_data[0:4]
                    frame_size = (ord(frame_header_data[4]) << 24) + (ord(frame_header_data[5]) << 16) + (ord(frame_header_data[6]) << 8) + (ord(frame_header_data[7]))
                    #print "  Frame ID: %s, size %d bytes" % (frame_id, frame_size)
                    total_read_size += 10 + frame_size
                    # Collect frame info
                    if   frame_id == "TALB":
                        self.v2_album  = f.read(frame_size)[1:]
                    elif frame_id == "TIT2":
                        self.v2_title  = f.read(frame_size)[1:]
                    elif frame_id == "TPE1":
                        self.v2_artist = f.read(frame_size)[1:]
                    elif frame_id == "TRCK":
                        self.v2_track  = int(f.read(frame_size)[1:].split('/')[0])
                    elif frame_id == "TYER":
                        self.v2_year   = int(f.read(frame_size)[1:])
                # clean the strings generated
                self.v2_title  = clean_string(self.v2_title)
                self.v2_artist = clean_string(self.v2_artist)
                self.v2_album  = clean_string(self.v2_album)
            else:
                print "No ID3v2 tag found."
                #self.v2_data_loaded = False


class MusicCollection:
    def __init__ (self):
        # Recursive function to create a multidimensional dictionary using defaultdict
        def create_multidimensional_dictionary (n, type):
            if n < 1:
                return type()
            return defaultdict(lambda:create_multidimensional_dictionary(n-1, type))
        # Create one
        self.albums = create_multidimensional_dictionary(2, list)
    
    
    def __str__ (self):
        s = "---- Album Dictionary Mappings ----\n"
        level_1_keys = self.albums.keys()
        for k1 in level_1_keys:
            level_2_keys = self.albums[k1].keys()
            for k2 in level_2_keys:
                s += "[%s][%s]\n" % (k1, k2)
                songs = self.albums[k1][k2]
                for song in songs:
                    s += "    %d %s\n" % (song.final_track, song.final_title)
        s += "-----------------------------------"
        return s


    # Creates a song from the MusicFile given and adds it to the song database. All the data from the 
    # MusicFile is compressed at this point.
    def add (self, music_file):
        if not music_file.final_data_set:
            raise Exception("create_song called with a non-finalised music file.")
        if not self.albums[music_file.final_artist][music_file.final_album]:
            self.albums[music_file.final_artist][music_file.final_album] = []
        self.albums[music_file.final_artist][music_file.final_album].append(music_file)




#-----------------------------------------------------------------------#
#-----------------    MUSICFILE SPECIFIC FUNCTIONS    ------------------#
#-----------------------------------------------------------------------#
# Takes a list of MusicFiles are expected to all come from the same album (and by extension artist) 
# and performs a vote between them to generate the correct album/artist information (if a majority 
# decision can be reached at all, if not it is assumed that these files do not in fact originate 
# from the same album).
def vote_on_album_between_music_files (music_file_list):
    # load the list of album names
    #for music_file in music_file_list:
    return




#-----------------------------------------------------------------------#
#--------------------    FILE HANDLING FUNCTIONS    --------------------#
#-----------------------------------------------------------------------#
# Strips extraneous whitespace and null bytes from some given data, leaving a string.
def strip_null_bytes (data):
    return data.replace("\00", "").strip()


# Packs a given string into a given number of bytes and null terminates it. This is
# achieved either by truncating (when too long) or adding null bytes (when too short).
def pack_null_bytes (string, length):
    if len(string) >= length-1:
        data = string[:length-1] + '\00'
    else:
        data = string + ('\00' * (length - len(string)))
    return data


# Writes the ID3v1.1 tag to a file (overwriting if present, appending if not).
def write_id3_v1_tag (input_file_path, output_song_data, output_file_path=""):
    global write_mode
    
    # if no output_file_path is given set it to the input_file_path (i.e. rewrite the input's tag).
    if output_file_path == "":
        output_file_path = input_file_path
    if output_file_path == input_file_path and not write_mode:
        raise Exception("write_id3_v1_tag called and instructed to write over the file, however write mode (-f) is not enabled.")
    
    # read the entire input file in.
    with open(input_file_path, "rb") as f:
        track_data = f.read()
    
    # check what existing id3v1 tag we have (if any), and if so purge it.
    if track_data[-128:-125] == "TAG":                      # check for v1.0/v1.1
        if track_data[-(128+227):-(128+227-4)] == "TAG+":   # check for v1.0 extended
            track_data = track_data[:-(128+227)]
        else:
            track_data = track_data[:-128]
    
    # create our new id3v1.1 tag and add it to the track data.
    genre = 255
    if output_song_data.album_year == 0:
        year_string = '\00' * 4
    else:
        year_string = str(output_song_data.album_year)
    # 3 B header, 30 B title, artist, album, 4 B year string, 28 B comment, zero-byte (signifying v1.1), 1 B track, 1 B genre
    new_tag = "TAG" + pack_null_bytes(output_song_data.track_name,  30) \
                    + pack_null_bytes(output_song_data.artist_name, 30) \
                    + pack_null_bytes(output_song_data.album_name,  30) \
                    + year_string                                       \
                    + '\00' * 28                                        \
                    + '\00'                                             \
                    + chr(output_song_data.track_number)                \
                    + chr(genre)                                        
    print "created new tag, size " + str(len(new_tag)) + " bytes"
    
    # write the result to the output file.
    track_data += new_tag
    with open(output_file_path, "wb") as f:
        f.write(track_data)


# Writes the ID3v2.x tag to a file (overwriting if present, inserting if not).
def write_id3_v2_tag (input_file_path, output_song_data, output_file_path=""):
    # Constructs an id3v2 text content frame using the frame_id given and the frame content (a string)
    def write_id3_v2_frame (frame_id, frame_content):
        size = len(frame_content) + 2       # encoding mark + content + null termination
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

    
    global write_mode
    # if no output_file_path is given set it to the input_file_path (i.e. rewrite the input's tag).
    if output_file_path == "":
        output_file_path = input_file_path
    if output_file_path == input_file_path and not write_mode:
        raise Exception("write_id3_v2_tag called and instructed to write over the file, however write mode (-f) is not enabled.")
    
    # read the entire input file in.
    with open(input_file_path, "rb") as f:
        track_data = f.read()
    
    # check what existing id3v2 tag we have (if any). if we have one, separate the track from it.
    had_id3v2_tag = False
    if track_data[:3] == "ID3":
        had_id3v2_tag = True
        # check its not messed up
        if ord(track_data[3]) == 0xFF or ord(track_data[4]) == 0xFF or ord(track_data[6]) >= 0x80 or ord(track_data[7]) >= 0x80 or ord(track_data[8]) >= 0x80 or ord(track_data[9]) >= 0x80:
            raise Exception("write_id3_v2_tag called on a file with a corrupted id3v2 tag. Exitting.")
        # Collect the tag header info. The tag_size is the complete ID3v2 tag size, minus the 
        # header (but not the extended header if one exists). Thus tag_size = total_tag_size - 10.
        tag_size = (ord(track_data[6]) << 21) + (ord(track_data[7]) << 14) + (ord(track_data[8]) << 7) + (ord(track_data[9]))
        tag_data   = track_data[:tag_size+10]
        track_data = track_data[tag_size+10:]
    
    # create a new tag and add our data to it
    # write the frames to it (we do this before we write the header so we can calculate the size)
    new_frames =  write_id3_v2_frame("TIT2", output_song_data.track_name)
    new_frames += write_id3_v2_frame("TALB", output_song_data.album_name)
    new_frames += write_id3_v2_frame("TPE1", output_song_data.artist_name)
    if output_song_data.track_number > 0:
        new_frames += write_id3_v2_frame("TRCK", str(output_song_data.track_number))
    if output_song_data.album_year > 0:
        new_frames += write_id3_v2_frame("TYER", str(output_song_data.album_year))
    # if we had an id3v2 tag before, copy the frames that we are not going to replace over from it. 
    # This leaves frames we aren't updating unchanged - an important consideration as some programs 
    # (i.e. windows media player) store their own data in them and in some cases the frames will 
    # store user data which will have taken some time to generate/collect, e.g. the POPM tag (though 
    # this is far from a standard itself).
    if had_id3v2_tag:
        total_read_size = 10
        while (total_read_size < tag_size+10):      # ONLY IF WE HAVE ONE DOOFUS
            if tag_data[total_read_size] == '\00':
                break
            frame_id = tag_data[total_read_size:total_read_size+4]
            frame_size = (ord(tag_data[total_read_size+4]) << 24) + (ord(tag_data[total_read_size+5]) << 16) + (ord(tag_data[total_read_size+6]) << 8) + (ord(tag_data[total_read_size+7]))
            # Note: This if statement could be extended to include other frames to be left out, or even
            # replaced with just PRIV frames (UFID and POPM should probably also be kept as they contain
            # information which will have been generated by other media players and is not easily
            # reproduceable). For now I have chosen to err on the side of caution and leave all other 
            # frames intact, but for a completely clean and identically tagged music collection this is
            # an option.
            if frame_id != "TALB" and frame_id != "TIT2" and frame_id != "TPE1" and frame_id != "TRCK" and frame_id != "TYER":
                new_frames += tag_data[total_read_size:total_read_size+10+frame_size]
            total_read_size += 10 + frame_size
    # calculate the size and add padding (I don't really like this approach, but I guess there's a 
    # reason all the tracks I tested include large amounts of padding so I will re-pad). Doing it at
    # this stage leaves the option to have the amount of padding added dependent on the tag size.
    # For now simply add 500 bytes of padding.
    #size = len(new_frames)
    new_frames += '\00' * 500
    size = len(new_frames)
    # produce the size string
    size_b1 = (size >> 21) % 128
    size_b2 = (size >> 14) % 128
    size_b3 = (size >>  7) % 128
    size_b4 = size         % 128
    size_string = chr(size_b1) + chr(size_b2) + chr(size_b3) + chr(size_b4)
    # write the header
    new_header =  "ID3"                # tag identifier
    new_header += chr(3) + chr(0)      # tag version number (v2.3.0)
    new_header += chr(0)               # flags
    new_header += size_string
    
    # write to the output file
    track_data = new_header + new_frames + track_data
    with open(output_file_path, "wb") as f:
        f.write(track_data)




#-----------------------------------------------------------------------#
#-------------------    STRING HANDLING FUNCTIONS    -------------------#
#-----------------------------------------------------------------------#
# for all words in the list, replace all but the last '.', all '_' and '-' with spaces, then remove 
# duplicate spaces before finally fixing the capitalisation.
def clean_string (s):
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
    
    return s


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
        #string_list[i] = word_list[i][0]
        
        previous_blank = 0
        if (word_list[i][0] == ""):
            previous_blank = 1
        
        for j in range(1, len(word_list[i])):
            if previous_blank == 0:
                #string_list[i] += " "
                return_list[i] += " "
            #string_list[i] += word_list[i][j]
            return_list[i] += word_list[i][j]
            
            previous_blank = 0
            if word_list[i][j] == "":
                previous_blank = 1
    
    #return string_list
    return return_list


# cleans all the files given to it (the cleaning only really makes sense per album folder).
def clean_folder (file_list):
    # create a cleaned copy of the file list
    cleaned_file_list = []
    for f in file_list:
        cleaned_file_list.append(clean_string(f))
    # remove the common words
    if len(file_list) > 1:
        cleaned_file_list = remove_common_words(cleaned_file_list)
    return cleaned_file_list




#-----------------------------------------------------------------------#
#---------------------------    MAIN CODE    ---------------------------#
#-----------------------------------------------------------------------#
# Parse command line arguments.
verbose_mode         = False
write_mode           = False
force_directory_mode = False
base_folder  = ""
if len(sys.argv) > 1:
    base_folder = sys.argv[1]
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "-v":
            verbose_mode = True
        elif sys.argv[i] == "-f":
            write_mode = True
        elif sys.argv[i] == "-d":
            force_directory_mode = True
# Check for a valid input. This doesn't check the base_folder's sanity.
if base_folder == "":
    print "Error: The program must be run on a folder, with the form:"
    print "./music_tagger FOLDER [options]"
    print "  -f - write changes."
    print "  -d - force the directory structure to be the ground truth, using its structure (artist/album/song.mp3) for the tag."
    print "  -v - verbose mode."
    print "System exiting."
    sys.exit()
if force_directory_mode == False:
    print "Error: Force directory mode (-d) is not enabled (i.e. you are telling the program you have a mismatched folder structure), however the functionality to deal with this scenario has not yet been implemented. Sorry!"
    sys.exit()

# create storage system
music_collection = MusicCollection()

# Traverse all folders (dirname gives the path to the current directory, dirnames gives the list of
# subdirectories in the folder, filenames gives the list of files in the folder). When mp3s are 
# located, build internal data for each file (from file system + id3 tags).
for dirname, subdirnames, filenames in os.walk(base_folder):
    music_list = []
    cleaned_filenames = clean_folder(filenames)
    for i in range(len(filenames)):
        if filenames[i][-4:] == ".mp3":
            # BOYZ WE FOUND OURSELF A SONG. Lets extract all the information possible from it and
            # add it to our database.
            file_path = os.path.join(dirname, filenames[i])
            new_file = MusicFile(file_path, cleaned_filenames[i])
            new_file.load_all_data()
            new_file.compress_all_data()
            music_collection.add(new_file)
print music_collection

# write the newly corrected data back to the tags

# write new data to file system


print "Finished."
