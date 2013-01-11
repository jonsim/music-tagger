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


CC=gcc -Wall

organize: organize.c common.o id3v1.o id3v2.o renamer.o
	$(CC) organize.c common.o id3v1.o id3v2.o renamer.o -o organize

common.o: common.c
	$(CC) -c common.c -o common.o

id3v1.o: id3v1.c
	$(CC) -c id3v1.c -o id3v1.o

id3v2.o: id3v2.c
	$(CC) -c id3v2.c -o id3v2.o

renamer.o: renamer.c
	$(CC) -c renamer.c -o renamer.o

clean:
	rm -f *.o organize
