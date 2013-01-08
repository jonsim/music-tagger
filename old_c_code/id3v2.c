#include "id3v2.h"

song* extractID3v2 (char* file_name)
{
	song* result = NULL;
	FILE *f;
	char  h[10];
	char* b;
	unsigned int tag_size = 0;
	unsigned int frame_size = 0;
	unsigned int bytes_read = 0;
	
	// open the file
	if ((f = fopen(file_name, "rb")) == NULL)
	{
		printf("No such file.\n");
		return NULL;
	}
	
	// if the file does not have a valid ID3v2 tag exit, otherwise read the header
	fread(h, 1, 10, f);
	if (strncmp(h, "ID3", 3) != 0)
	{
		fclose(f);
		printf("Track does not have a valid ID3v2 tag.\n");
		return NULL;
	}
	
	// calculate tag size from the header
	tag_size = (h[6] * (1<<21)) + (h[7] * (1<<14)) + (h[8] * (1<<7)) + h[9];
	printf("\nTrack has ID3v2.%u.%u (%u bytes)\n", h[3], h[4], tag_size);
	if (h[5] & 0x40)
		printf("extended header\n");
	
	// read tags until there are no more available/valid
	result = calloc(1, sizeof(song));
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
		
		// title frame
		if      (strncmp(h, "TIT2", 4) == 0)
		{
			result->title = calloc(frame_size + 1, sizeof(char));
			charCopy(result->title, b, frame_size);
		}
		// lead artist(s) frame
		else if (strncmp(h, "TPE1", 4) == 0)
		{
			if (result->artist == NULL)
			{
				result->artist = calloc(frame_size + 1, sizeof(char));
				charCopy(result->artist, b, frame_size);
			}
		}
		// band frame
		else if (strncmp(h, "TPE2", 4) == 0)
		{
			if (result->artist == NULL)
			{
				result->artist = calloc(frame_size + 1, sizeof(char));
				charCopy(result->artist, b, frame_size);
			}
		}
		// album frame
		else if (strncmp(h, "TALB", 4) == 0)
		{
			result->album = calloc(frame_size + 1, sizeof(char));
			charCopy(result->album, b, frame_size);
		}
		// year frame
		else if (strncmp(h, "TYER", 4) == 0)
		{
			result->year = calloc(frame_size + 1, sizeof(char));
			charCopy(result->year, b, frame_size);
		}
		// track frame
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
		// content (genre) frame
		else if (strncmp(h, "TCON", 4) == 0)
		{
			result->genre = calloc(frame_size + 1, sizeof(char));
			charCopy(result->genre, b, frame_size);
		}
	}
	
	fclose(f);
	return result;
}



