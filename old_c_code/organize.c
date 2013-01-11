/*-----------------------------------------------------------------------*/
/*----------------------------    LICENSE    ----------------------------*/
/*-----------------------------------------------------------------------*/
/* This file is part of the music_tagger program                         */
/* (https://github.com/jonsim/music_tagger).                             */
/*                                                                       */
/* music_tagger is free software: you can redistribute it and/or modify  */
/* it under the terms of the GNU General Public License as published by  */
/* the Free Software Foundation, either version 3 of the License, or     */
/* (at your option) any later version.                                   */
/*                                                                       */
/* music_tagger is distributed in the hope that it will be useful,       */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of        */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         */
/* GNU General Public License for more details.                          */
/*                                                                       */
/* You should have received a copy of the GNU General Public License     */
/* along with music_tagger.  If not, see <http://www.gnu.org/licenses/>. */
/*-----------------------------------------------------------------------*/


/*-----------------------------------------------------------------------*/
/*----------------------------     ABOUT     ----------------------------*/
/*-----------------------------------------------------------------------*/
/* A small program to tidy music files. It recursively explores a given  */
/* directory and standardises folder structures, file naming conventions */
/* and ID3 tags.                                                         */
/* Author: Jonathan Simmonds                                             */
/*-----------------------------------------------------------------------*/


/*-----------------------------------------------------------------------*/
/*---------------------------    INCLUDES    ----------------------------*/
/*-----------------------------------------------------------------------*/
#include "id3v1.h"
#include "id3v2.h"
#include "renamer.h"




/*-----------------------------------------------------------------------*/
/*-------------------------    MAIN FUNCTION    -------------------------*/
/*-----------------------------------------------------------------------*/
int main (int argc, char **argv)
{
/*	song* song;
	song = extractID3v1 (argv[1]);
	if (song != NULL)
		printf("\nTrack has ID3v1 tag:\n\ntitle  = %s\nartist = %s\nalbum  = %s\nyear   = %s\ntrack  = %s / %s\ngenre  = %d\n\n", song->title, song->artist, song->album, song->year, song->track, song->max_tracks, *song->genre);
	
	song = NULL;
	song = extractID3v2 (argv[1]);
	if (song != NULL)
		printf("\ntitle  = %s\nartist = %s\nalbum  = %s\nyear   = %s\ntrack  = %s / %s\ngenre  = %s\n\n", song->title, song->artist, song->album, song->year, song->track, song->max_tracks, song->genre);*/
	
	list* a = NULL;
	list* b = NULL;
	int split_len = -1, i;
	splitlist** c;
	
	a = loadFolders(".");
	printf("Read folders into a.\n");
	
	readDirectory(&b, &a);
	printf("\nRead directory into b:\n");
	printListAligned(b);
	printf("\nRemaining files in a:\n");
	printListAligned(a);
	
	renameFiles(&b);
	printf("\nRenamed files in b:\n");
	printListAligned(b);
	
	
	c = splitAll(b, ' ', &split_len);
	printf("\nSplit all %d file names in b:\n", split_len);
	for (i = 0; i < split_len; i++)
	{
		printSplit(c[i]);
		putchar('\n');
	}
	putchar('\n');
	removeCommonWords(c, split_len);
	printf("\nRemoved common words from b:\n");
	for (i = 0; i < split_len; i++)
	{
		printSplit(c[i]);
		putchar('\n');
	}
	
	
	
	return 0;
}
