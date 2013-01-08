music_tagger
============

A small program to tidy music files. It recursively explores a given directory and standardises folder structures, file naming conventions and ID3 tags.

NB: I also have a small test directory structure containing a sample of music files in the repository, however for copyright reasons I have not committed them. Should you want to clone the project I would recommend that you replicate this setup by copying a few albums into the repository for testing purposes.

TODO:
- Add the ability to write ID3v1 + ID3v2 tags. This will also need to be able to insert the tags if they are missing, not just modify them.
- Add some type of voting procedure to decide on the correct album/artist/track name from the available information (file path, ID3v1 tag, ID3v2 tag).

EXTENSIONS:
It would be nice to be able to have the program produce several versions of the file at different bit rates for different device usage (e.g. mobile devices would take 196 kbps, desktop devices would take 320 kbps)
