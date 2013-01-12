Music Tagger
============

A small program to tidy music files. It recursively explores a given directory and standardises 
folder structures, file naming conventions and ID3 tags.


In Depth
--------
NOTE THIS IS A WORK IN PROGRESS AND AS SUCH SOME OF THE FEATURES MENTIONED BELOW ARE NOT YET 
IMPLEMENTED.

In more detail, the program recursively explores a given directory tree and, for each song it finds 
extracts data about it from three different potential sources:
 - The file path when it is of the form "ARTIST/ALBUM/SONG.mp3", where ALBUM can optionally include 
   a year and SONG can optionally include a track number. All folder/file names are cleaned to fix 
   capitalisation issues and any symbols (e.g. for-example and FOR.EXAMPLE).
 - The ID3v1 tag (accepting: v1.0 / v1.1 / extended versions of either).
 - The ID3v2 tag (accepting: v2.2.x / v2.3.x / v2.4.x).
This data is collected and then merged together based on string similarity (hopefully removing 
errors such as the addition of " EP" to the end of album names and general typos). A voting 
procedure is then undertaken between files from the same folder in order to standardise artist/album 
names across them (e.g. "AC/DC" "ACDC" "AC DC" "AC-DC"), although no change will be effected when 
this is not possible (e.g. compilation CDs or a single folder containing the user's entire music 
collection).

Finally this amalgamated and standardised information is applied back to the files to write both 
ID3v1.1 and ID3v2.3.0 tags to them (by far the most common and flexible). Old tag data will not be 
deleted in order to preserve player preferences and settings (e.g. some players store the user's 
song rating in the ID3 tag).
Additionally changes will be made to the directory (as a dry-run by default) tree, renaming files to
the form "TRACKNUM TITLE.mp3". The directory names are also updated to accommodate the new names 
(e.g. fixing misspelled album/artist names). An option is available to create a new folder structure
in the form "ARTIST/ALBUM/SONG.mp3", should one not already exist. Compilation CDs will be 
identified and stored in "Various Artists/ALBUM/SONG.mp3" and will not be separated.

© Copyright 2013 Jonathan Simmonds


License
-------
The project is released under the GPLv3 license.


To Do
-----
- Add some type of voting procedure to decide on the correct album/artist name from files within the
  same folder.
- Add a method to rename files and folders.
- Add a method to create a new folder structure.
- Add a method to detect compilation CDs when indexing and avoid scattering these items around.
- It would be nice to be able to have the program produce several versions of the file at different 
bit rates for different device usage (e.g. mobile devices would take 128-196 kbps, desktop devices 
would take 320 kbps).

Note: I also have a small test directory structure containing a few sample music files in the 
repository, however for copyright reasons I have not committed them. Should you want to work on the 
project I would recommend that you replicate this setup by copying a few albums into the repository 
for testing purposes.
