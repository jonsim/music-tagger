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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STACKSIZE 256
#define WORDSIZE 256

typedef struct 
{
	char* title;
	char* artist;
	char* album;
	char* year;
	char* track;
	char* max_tracks;
	char* genre;
} id3;


int containsCharacter (char* s, char c, int len)
{
	int i;
	for (i = 0; i < len; i++)
		if (s[i] == c)
			return i;
	return -1;
}



void charCopy (char* out, char* in, int len)
{
	int i;
	for (i = 0; in[0] == 0; i++)
		in++;
	for (i = 0; i < len; i++)
		out[i] = in[i];
	out[i] = '\0';
}



id3* extractID3v2 (char* file_name)
{
	id3* result = NULL;
	FILE *f;
	char  h[10];
	char* b;
	unsigned int tag_size = 0;
	unsigned int frame_size = 0;
	unsigned int bytes_read = 0;
//	int i;
	
	// open the file
	if ((f = fopen(file_name, "rb")) == NULL)
	{
		printf("No such file.\n");
		return NULL;
	}
	
	// read the 10 byte header to see if its an id3v2 tag. if not, exit
	fread(h, 1, 10, f);
	if (strncmp(h, "ID3", 3) == 0)
	{
		// calculate tag size from the header
		tag_size = (h[6] * (1<<21)) + (h[7] * (1<<14)) + (h[8] * (1<<7)) + h[9];
		printf("\nTrack has ID3v2.%u.%u (%u bytes)\n", h[3], h[4], tag_size);
		if (h[5] & 0x40)
			printf("extended header\n");
	}
	else
	{
		printf("Track does not have a valid ID3v2 tag.\n");
		fclose(f);
		return NULL;
	}
	
	// read tags until there are no more available/valid
	result = calloc(1, sizeof(id3));
	while (bytes_read < tag_size)
	{
		// extract the tag header and exit if not all of it can be read
		if (fread(h, 1, 10, f) < 10)
			break;
		bytes_read += 10;
			
		// calculate frame size from the header, and exit if invalid
		frame_size = (h[4] & 0xFF) * (1<<24) + (h[5] & 0xFF) * (1<<16) + (h[6] & 0xFF) * (1<<8) + (h[7] & 0xFF);
		if (frame_size < 1)
			break;
		
		// extract the tag body and exit if not all of it can be read
		b = calloc(frame_size, sizeof(char));
		if (fread(b, 1, frame_size, f) < frame_size)
			break;
		bytes_read += frame_size;
		
		// save the tag body as necessary
		if      (strncmp(h, "TIT2", 4) == 0)
		{
			result->title = calloc(frame_size + 1, sizeof(char));
			charCopy(result->title, b, frame_size);
		}
		else if (strncmp(h, "TPE1", 4) == 0)
		{
			if (result->artist == NULL)
			{
				result->artist = calloc(frame_size + 1, sizeof(char));
				charCopy(result->artist, b, frame_size);
			}
		}
		else if (strncmp(h, "TPE2", 4) == 0)
		{
			if (result->artist == NULL)
			{
				result->artist = calloc(frame_size + 1, sizeof(char));
				charCopy(result->artist, b, frame_size);
			}
		}
		else if (strncmp(h, "TALB", 4) == 0)
		{
			result->album = calloc(frame_size + 1, sizeof(char));
			charCopy(result->album, b, frame_size);
		}
		else if (strncmp(h, "TYER", 4) == 0)
		{
			result->year = calloc(frame_size + 1, sizeof(char));
			charCopy(result->year, b, frame_size);
		}
		else if (strncmp(h, "TRCK", 4) == 0)
		{
			int slash = containsCharacter(b, '/', frame_size);
			if (slash > -1)
			{
				result->track = calloc(slash, sizeof(char));
				charCopy(result->track, b, slash - 1);
				
				b += slash;
				result->max_tracks = calloc(frame_size - slash + 1, sizeof(char));
				charCopy(result->max_tracks, b, frame_size - slash);
			}
			else
			{
				result->track = calloc(frame_size + 1, sizeof(char));
				charCopy(result->track, b, frame_size);
			}
		}
		else if (strncmp(h, "TCON", 4) == 0)
		{
			result->genre = calloc(frame_size + 1, sizeof(char));
			charCopy(result->genre, b, frame_size);
		}
	}
	
	fclose(f);
	return result;
}


id3* extractID3v1 (char* file_name)
{
	FILE *f;
	char buffer[256];
	
	// open the file, load its contents to the buffer and close it
	if ((f = fopen(file_name, "rb")) == NULL)
	{
		printf("No such file.\n");
		return NULL;
	}
	fseek(f, -128L, SEEK_END);
	fread(buffer,1,128,f);
	fclose(f);
	
	// if the file has the TAG flag, read the contents out
	if (strncmp(buffer, "TAG", 3) == 0)
	{
		char* str_bgn;
		int str_len;
		id3* result = calloc(1, sizeof(id3));
		
		// extract title
		str_bgn = buffer  +  3;
		str_len = 30;
		while (str_len > 0 && str_bgn[str_len - 1] == ' ')
			str_len--;
		if (str_len > 0)
		{
			result->title = calloc(str_len + 1, sizeof(char));
			strncpy(result->title, str_bgn, str_len);
			result->title[str_len] = '\0';
		}
		
		// extract artist
		str_bgn = buffer  + 33;
		str_len = 30;
		while (str_len > 0 && str_bgn[str_len - 1] == ' ')
			str_len--;
		if (str_len > 0)
		{
			result->artist = calloc(str_len + 1, sizeof(char));
			strncpy(result->artist, str_bgn, str_len);
			result->artist[str_len] = '\0';
		}
		
		// extract album
		str_bgn = buffer  + 63;
		str_len = 30;
		while (str_len > 0 && str_bgn[str_len - 1] == ' ')
			str_len--;
		if (str_len > 0)
		{
			result->album = calloc(str_len + 1, sizeof(char));
			strncpy(result->album, str_bgn, str_len);
			result->album[str_len] = '\0';
		}
		
		// extract year
		str_bgn = buffer  + 93;
		str_len = 4;
		result->year = calloc(str_len + 1, sizeof(char));
		strncpy(result->year, str_bgn, str_len);
		result->year[str_len] = '\0';
		
		// extract track
		if (buffer[125] == 0)
		{
			result->track = calloc(3, sizeof(char));
//			itoa((int) buffer[126], result->track);
			sprintf(result->track, "%d", buffer[126]);
		}
				
		//extract genre
		result->genre = calloc(1, sizeof(char));
		*result->genre = buffer[127];
		
		return result;
	}
	else
	{
		printf("Track does not have a valid ID3v1 tag.\n");
		return NULL;
	}
}



/*////////// MAIN FUNCTION //////////*/

int main (int argc, char **argv)
{
	id3* song;
	song = extractID3v1 (argv[1]);
	if (song != NULL)
		printf("\nTrack has ID3v1 tag:\n\ntitle  = %s\nartist = %s\nalbum  = %s\nyear   = %s\ntrack  = %s / %s\ngenre  = %d\n\n", song->title, song->artist, song->album, song->year, song->track, song->max_tracks, *song->genre);
	
	song = NULL;
	song = extractID3v2 (argv[1]);
	if (song != NULL)
		printf("\ntitle  = %s\nartist = %s\nalbum  = %s\nyear   = %s\ntrack  = %s / %s\ngenre  = %s\n\n", song->title, song->artist, song->album, song->year, song->track, song->max_tracks, song->genre);
	
	return 0;
}

