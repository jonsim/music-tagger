#include "id3v1.h"

song* extractID3v1 (char* file_name)
{
	FILE *f;
	song* result;
	char buffer[256];
	char* str_bgn;
	int str_len;
	
	// open the file, load the last 128 bytes to the buffer and close it
	if ((f = fopen(file_name, "rb")) == NULL)
	{
		printf("No such file.\n");
		return NULL;
	}
	fseek(f, -128L, SEEK_END);
	fread(buffer,1,128,f);
	fclose(f);
	
	// if the file does not have a valid ID3v1 tag exit, otherwise read it
	if (strncmp(buffer, "TAG", 3) != 0)
	{
		printf("Track does not have a valid ID3v1 tag.\n");
		return NULL;
	}

	result = calloc(1, sizeof(song));
	
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
		sprintf(result->track, "%d", buffer[126]);
	}
			
	//extract genre
	result->genre = calloc(1, sizeof(char));
	*result->genre = buffer[127];
	
	return result;
}
