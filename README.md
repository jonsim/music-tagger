music_tagger
============

A small program to tidy music files. It recursively explores a given directory and standardises 
folder structures, file naming conventions and ID3 tags.

In more detail, the program should explore a given directory and extract song information from the 
folder structure (if it is artist/album/song.mp3), the file name and any applicable ID3 tags (either 
v1 or v2 or both). The correct information (from these three potential sources) is then decided upon 
before the folder structure is updated (to artist/album/song.mp3), the file renamed appropriately 
(to "TRACKNUM Song Title.mp3") and is correctly tagged (with both an ID3v1.1 and an ID3v2.3.0 tag).

Note: I also have a small test directory structure containing a few sample music files in the 
repository, however for copyright reasons I have not committed them. Should you want to work on the 
project I would recommend that you replicate this setup by copying a few albums into the repository 
for testing purposes.

© Copyright 2013 Jonathan Simmonds


License
-------
The project is released under the GPLv3 license. It is created by Jonathan Simmonds.


To Do
-----
- Add some type of voting procedure to decide on the correct album/artist/track name from the 
available information (file path, ID3v1 tag, ID3v2 tag).
- Add a method to create a new folder structure and rename files.


Extensions
----------
- It would be nice to be able to have the program produce several versions of the file at different 
bit rates for different device usage (e.g. mobile devices would take 128-196 kbps, desktop devices 
would take 320 kbps).
