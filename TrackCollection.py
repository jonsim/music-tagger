"""Imports:
    defaultdict: for multidimensional dictionaries (implicitly instantiating
        the nested dictionaries as the dimensions are accessed)
    operator: sorting dictionaries
    os: writing the collection out to disk
"""
from collections import defaultdict
import operator
import os

class TrackCollection(object):
    """A structure sorting tracks by artist and album

    Attributes:
        file_count: int number of files in this collection
        collection: 2-dimensional defaultdict of all tracks namespaced by artist
            then album
    """
    file_count = 0

    def __init__(self):
        def create_multidimensional_dict(n, dict_type):
            """Recursive function to create a multidimensional defaultdict

            Args:
                n: int dimensionality of the defaultdict
                dict_type: type of the elements

            Returns:
                A multidimensional defaultdict"""
            if n < 1:
                return dict_type()
            return defaultdict(lambda: create_multidimensional_dict(n-1, dict_type))
        # Create one.
        self.collection = create_multidimensional_dict(2, list)


    def __str__(self):
        s = "---- Album Dictionary Mappings ----\n"
        # List artists and sort
        artists = self.collection.keys()
        artists.sort()
        for artist in artists:
            # List albums and sort
            albums = self.collection[artist].keys()
            albums.sort(key=lambda k2, k1=artist: self.collection[k1][k2][0].final.year)
            for album in albums:
                s += "[%s][%s]\n" % (artist, album)
                for song in self.collection[artist][album]:
                    s += "  %02d %s\n" % (song.final.track, song.final.title)
        s += "-----------------------------------"
        return s


    def add(self, track):
        """Adds a TrackFile to the collection.

        Args:
            track: A TrackFile to add. Must be finalised at this point (for
                indexing purposes).

        Returns:
            None

        Raises:
            Exception: The given track was not finalised.
        """
        # TODO Compilations are going to wreak havoc here too, see note on
        # remove_duplicates.
        if not track.finalised:
            raise Exception("TrackCollection cannot add a non-finalised track")
        if not self.collection[track.final.artist][track.final.album]:
            self.collection[track.final.artist][track.final.album] = []
        self.collection[track.final.artist][track.final.album].append(track)
        self.file_count += 1


    def remove_duplicates(self, warnings=None, report_progress=None):
        """Look for duplicate songs and remove them.

        Duplicate artists and albums are not a problem - you need a music file
        (itself a song) to contain the data to have generated them, so you
        either have duplicate songs, or different songs with slightly different
        artist/album names. This should be corrected by the TrackFile's
        compression step. If it wasn't properly picked up then (i.e. the names
        were too dissimilar) we have no further information at this point so we
        can't fix it.

        Args:
            report_progress: Optional two argument function to report progress
                where the first argument is the total number of items and the
                second argument is the completed number of items.

        Returns:
            None
        """
        # TODO: Compilations are going to go crazy here... revist this later,
        # probably with a TrackFile flag for (probable) compilation tracks.
        processed_count = 0
        for artist in self.collection:
            for album in self.collection[artist]:
                duplicate_tracker = {}
                to_be_removed = []
                for song in self.collection[artist][album]:
                    title = song.final.title
                    # If a track with this title already exists within this
                    # artist/album tuple, mark it as a duplicate (and optionally
                    # generate a warning
                    if title in duplicate_tracker:
                        duplicate = duplicate_tracker[title]
                        if warnings is not None and ( \
                                duplicate.final.track != song.final.track or \
                                duplicate.final.year != song.final.year):
                            warnings.append('Found songs with the same artist, ' \
                                'album and title but differing track or year:\n' \
                                '  %s\n    %s\n  %s\n    %s' % ( \
                                    duplicate, duplicate.file_path, \
                                    song, song.file_path))
                        to_be_removed.append(song)
                    else:
                        duplicate_tracker[title] = song
                    processed_count += 1
                    if report_progress:
                        report_progress(self.file_count, processed_count)
                for song in to_be_removed:
                    self.collection[artist][album].remove(song)
                self.file_count -= len(to_be_removed)


    def standardise_album_tracks(self, warnings=None, report_progress=None):
        """Standardises track data between tracks within each album.

        Takes a vote between tracks within albums to standardise information on
        the album year and track numbering.

        Args:
            report_progress: Optional two argument function to report progress
                where the first argument is the total number of items and the
                second argument is the completed number of items.

        Returns:
            None
        """
        # TODO Compilations are going to wreak havoc here too, see note on
        # remove_duplicates.
        processed_count = 0
        for artist in self.collection:
            for album in self.collection[artist]:
                # First collect the number of times each different album year
                # data appears. Ideally all tracks should have the same year.
                album_year_votes = {}
                for song in self.collection[artist][album]:
                    if song.final.year in album_year_votes:
                        album_year_votes[song.final.year] += 1
                    else:
                        album_year_votes[song.final.year] = 1
                    processed_count += 1
                    if report_progress:
                        report_progress(self.file_count, processed_count)
                # If there is more than one album year listed, standardise. A
                # good argument could be made for any number of strategies for
                # standardising. Currently the majority vote takes it, but the
                # latest 'sensible' year would also be an idea.
                if len(album_year_votes.keys()) > 1:
                    sorted_album_year_votes = sorted(album_year_votes.iteritems(),
                                                     key=operator.itemgetter(1),
                                                     reverse=True)
                    if sorted_album_year_votes[0][0] != 0:
                        correct_year = sorted_album_year_votes[0][0]
                    else:
                        correct_year = sorted_album_year_votes[1][0]
                    if warnings is not None:
                        warnings.append('Multiple album years for %s ' \
                            'by %s: %s. Using %d.' \
                            % (album, artist, str(sorted_album_year_votes), correct_year))
                    for song in self.collection[artist][album]:
                        song.final.year = correct_year


    def sort_songs_by_track(self):
        """Sort the songs in the lists by their track numbers.

        Returns:
            None
        """
        for artist in self.collection:
            for album in self.collection[artist]:
                self.collection[artist][album].sort(key=lambda x: x.final.track)


    def create_new_filesystem(self, new_path):
        """Creates a collection starting from a root directory.

        Args:
            new_path: The path to recursively search for the collection within.

        Returns:
            None
        """
        os.mkdir(new_path)
        for artist in self.collection:
            artist_subpath = '/%s' % (artist)
            os.mkdir(new_path + artist_subpath)
            for album in self.collection[artist]:
                if self.collection[artist][album][0].final.year != 0:
                    album_subpath = '/[%d] %s' % (self.collection[artist][album][0].final.year, album)
                else:
                    album_subpath = '/%s' % (album)
                os.mkdir(new_path + artist_subpath + album_subpath)
                for song in self.collection[artist][album]:
                    song_subpath = '/%02d %s.mp3' % (song.final.track, song.final.title)
                    create_new_file(song, new_path + artist_subpath + album_subpath + song_subpath)
