import TrackData, ID3v1Parser, ID3v2Parser, FilePathParser
import Levenshtein

class TrackFile:
    # File path, the only required and certain piece of data.
    file_path = ""
    cleaned_filename = ""
    finalised = False
    # Data extracted from the file path.
    fp = None
    # Data extracted from the ID3v1 tag.
    v1 = None
    # Data extracted from the ID3v2 tag.
    v2 = None
    # Final data.
    final = None
    
    def __init__(self, file_path, cleaned_filename=""):
        """ Creates the TrackFile object.
        
        Args:
            file_path: String path to the music file.
            cleaned_filename: File name removed of any unnecessary data.
                Optional argument. Opting not to provide it will cause the
                cleaned filename to be generated automatically. The downside of
                this is that when automatic cleaning of the filename occurs it
                is treated in isolation to all other files in the directory (as
                it does not have access to them) so it cannot perform common
                word removal or other similar, contextual techniques.
        
        Returns:
            The initialised TrackFile object.
        """
        if file_path == "":
            raise Exception("Cannot create a TrackFile with an empty file_path.")
        self.file_path = file_path
        if cleaned_filename == "":
            self.cleaned_filename = clean_string(file_path.split('/')[-1], True)
        else:
            self.cleaned_filename = cleaned_filename
    
    
    def __str__(self):
        if self.finalised:
            s = str(self.final)
        else:
            s = "TrackFile uncompressed data:\n"
            s += "  fp) %s\n" % (self.fp)
            s += "  v1) %s\n" % (self.v1)
            s += "  v2) %s"   % (self.v2)
        return s
    
    
    def load_all_data(self):
        """ Loads TrackData for the file from all available sources.

        Returns:
            None
        """
        self.fp = FilePathParser.read_file_path_data(self.file_path, self.cleaned_filename)
        self.v1 = ID3v1Parser.read_id3v1_tag_data(self.file_path)
        self.v2 = ID3v2Parser.read_id3v2_tag_data(self.file_path)
    
    
    def finalise_data(self):
        """ Generates the finalised data from all currently loaded sources.
        
        This is done by a voting procedure between all loaded sources. These
        loaded sources may be from filename parsing, an ID3v1 tag, an ID3v2 tag.
        Does not delete any of the old data, however the finalised flag is set
        which will cause other functions to read only this final data from the
        object. Many functions which act on the TrackFile require this
        finalisation to have taken place.
        
        Returns:
            None
        """
        def finalise_str (fp=None, v1=None, v2=None):
            """ Produces a single piece of string data from those provided.
            
            Args:
                fp: Optional string representing data from file path parsing.
                v1: Optional string representing data from an ID3v1 tag.
                v2: Optional string representing data from an ID3v2 tag
            
            Returns:
                A string best guess at the data from that provided.
            """
            # We tend to favour fp while v1 and v2 have equal weighting. We
            # assume v1 could have been truncated to 30 characters (hence why,
            # when it is compared with other strings they have to be cut down
            # and it is never directly returned).
            fp_v1_distance = 0
            fp_v2_distance = 0
            v1_v2_distance = 0
            DISTANCE_THRESHOLD = 3
            if fp and v1:
                fp_v1_distance = Levenshtein.distance(fp[:30], v1)
            if fp and v2:
                fp_v2_distance = Levenshtein.distance(fp,      v2)
            if v1 and v2:
                v1_v2_distance = Levenshtein.distance(v1,      v2[:30])
            
            # If fp is similar to one of them, return fp. Otherwise if v1 and v2
            # are similar, return v2. Otherwise just return fp (as good as
            # random chance - something should probably be printed).
            if (fp and v1 and (fp_v1_distance < DISTANCE_THRESHOLD)) or (fp and v2 and (fp_v2_distance < DISTANCE_THRESHOLD)):
                return fp
            elif v1 and v2 and (v1_v2_distance < DISTANCE_THRESHOLD):
                return v2
            elif fp:
                return fp
            elif v2:
                return v2
            elif v1:
                return v1
            else:
                # All string data is essential - raise an exception if missing.
                raise Exception("finalise_str called with no readable arguments.")
        
        def finalise_int (fp=None, v1=None, v2=None):
            """ Produces a single piece of integer data from those provided.
            
            Args:
                fp: Optional int representing data from file path parsing.
                v1: Optional int representing data from an ID3v1 tag.
                v2: Optional int representing data from an ID3v2 tag
            
            Returns:
                An int best guess at the data from that provided.
            """
            if (fp and v1 and (fp == v1)) or (fp and v2 and (fp == v2)):
                return fp
            elif v1 and v2 and (v1 == v2):
                return v2
            elif fp:
                return fp
            elif v2:
                return v2
            elif v1:
                return v1
            else:
                # Integer data is non-essential.
                return 0
        
        final = TrackData.TrackData()
        final.title  = finalise_str(self.fp.title,  self.v1.title,  self.v2.title)
        final.album  = finalise_str(self.fp.album,  self.v1.album,  self.v2.album)
        final.artist = finalise_str(self.fp.artist, self.v1.artist, self.v2.artist)
        final.track  = finalise_int(self.fp.track,  self.v1.track,  self.v2.track)
        final.year   = finalise_int(self.fp.year,   self.v1.year,   self.v2.year)
        final.genre  = finalise_int(None,           self.v1.genre,  self.v2.genre)
        self.final = final
        self.finalised = True

