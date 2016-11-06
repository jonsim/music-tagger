from collections import defaultdict
import operator
import TrackFile

class TrackCollection:
    file_count = 0
    
    def __init__(self):
        # Recursive function to create a multidimensional dict using defaultdict
        def create_multidimensional_dict (n, type):
            if n < 1:
                return type()
            return defaultdict(lambda:create_multidimensional_dict(n-1, type))
        # Create one.
        self.albums = create_multidimensional_dict(2, list)
    
    
    def __str__(self):
        s =  "---- Album Dictionary Mappings ----\n"
        for k1 in self.albums.keys():
            for k2 in self.albums[k1].keys():
                s += "[%s][%s]\n" % (k1, k2)
                for song in self.albums[k1][k2]:
                    s += "  %02d %s\n" % (song.final.track, song.final.title)
        s += "-----------------------------------"
        return s


    def add(self, track):
        """ Adds a TrackFile to the collection.
        
        Args:
            track: A TrackFile to add. Must be finalised at this point (for
                indexing purposes).

        Returns:
            None
        """
        # TODO Compilations are going to wreak havoc here too, see note on
        # remove_duplicates.
        if not track.finalised:
            raise Exception("add called with a non-finalised track")
        if not self.albums[track.final.artist][track.final.album]:
            self.albums[   track.final.artist][track.final.album] = []
        self.albums[       track.final.artist][track.final.album].append(track)
        self.file_count += 1
    
    
    def remove_duplicates(self):
        """ Look for duplicate songs and remove them.
        
        Duplicate artists and albums are not a problem - you need a music file
        (itself a song) to contain the data to have generated them, so you
        either have duplicate songs, or different songs with slightly different
        artist/album names. This should be corrected by the TrackFile's
        compression step. If it wasn't properly picked up then (i.e. the names
        were too dissimilar) We have no further information at this point so we
        can't fix it.

        Returns:
            None
        """
        # TODO: Compilations are going to go crazy here... revist this later,
        # probably with a TrackFile flag for (probable) compilation tracks.
        for k1 in self.albums.keys():
            for k2 in self.albums[k1].keys():
                duplicate_tracker = {}
                to_be_removed = []
                for song in self.albums[k1][k2]:
                    k3 = song.final.title
                    if k3 in duplicate_tracker:
                        if duplicate_tracker[k3].final.track != song.final.track or duplicate_tracker[k3].final.year != song.final.year:
                            #print "WARNING: Songs with duplicate artist, album and title found (at %s and %s) but differing track (%d vs %d) and/or year (%d vs %d) data. Keeping the first." % (duplicate_tracker[k3].file_path, song.file_path, duplicate_tracker[k3].final.track, song.final.track, duplicate_tracker[k3].final.year, song.final.year)
                            print "WARNING: Songs with duplicate information found:"
                            print "  %s:%s" % ('{:<80}'.format(duplicate_tracker[k3].file_path), duplicate_tracker[k3])
                            print "  %s:%s" % ('{:<80}'.format(song.file_path), song)
                        to_be_removed.append(song)
                    else:
                        duplicate_tracker[k3] = song
                [self.albums[k1][k2].remove(song) for song in to_be_removed]
    
    
    def standardise_album_tracks(self):
        """ Standardises track data between tracks within each album.
        
        Takes a vote between tracks within albums to standardise information on
        the album year and track numbering.
        
        Returns:
            None
        """
        # TODO Compilations are going to wreak havoc here too, see note on
        # remove_duplicates.
        # Pass through all the songs
        for k1 in self.albums.keys():
            for k2 in self.albums[k1].keys():
                # First collect the number of times each different album year data appears. Ideally 
                # all tracks should have the same year.
                album_year_votes = {}
                for song in self.albums[k1][k2]:
                    if song.final.year in album_year_votes:
                        album_year_votes[song.final.year] += 1
                    else:
                        album_year_votes[song.final.year] =  1
                # If there is more than one album year listed, standardise. A good argument could be
                # made for any number of strategies for standardising. Currently the majority vote
                # takes it, but the latest 'sensible' year would also be an idea.
                if len(album_year_votes.keys()) > 1:
                    sorted_album_year_votes = sorted(album_year_votes.iteritems(), key=operator.itemgetter(1), reverse=True)
                    if sorted_album_year_votes[0][0] != 0:
                        correct_year = sorted_album_year_votes[0][0]
                    else:
                        correct_year = sorted_album_year_votes[1][0]
                    print "WARNING: multiple album year votes found for %s by %s: %s. Using %d." % (k2, k1, str(sorted_album_year_votes), correct_year )
                    for song in self.albums[k1][k2]:
                        song.final.year = correct_year
    
    
    def sort_songs_by_track (self):
        """ Sort the songs in the lists by their track numbers.
        
        Returns:
            None
        """
        for k1 in self.albums.keys():
            for k2 in self.albums[k1].keys():
                self.albums[k1][k2].sort(key=lambda x: x.final.track)
    
    
    def create_new_filesystem (self, new_path):
        """ Creates a collection starting from a root directory.
        
        Args:
            new_path: The path to recursively search for the collection within.
        
        Returns:
            None
        """
        os.mkdir(new_path)
        for artist_name in self.albums.keys():
            artist_subpath = '/%s' % (artist_name)
            os.mkdir(new_path + artist_subpath)
            for album_name in self.albums[artist_name].keys():
                if self.albums[artist_name][album_name][0].final.year != 0:
                    album_subpath = '/[%d] %s' % (self.albums[artist_name][album_name][0].final.year, album_name)
                else:
                    album_subpath = '/%s' % (album_name)
                os.mkdir(new_path + artist_subpath + album_subpath)
                for song in self.albums[artist_name][album_name]:
                    song_subpath = '/%02d %s.mp3' % (song.final.track, song.final.title)
                    create_new_file(song, new_path + artist_subpath + album_subpath + song_subpath)

