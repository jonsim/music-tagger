#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <dirent.h>

#ifndef COMMON_H
#include "common.h"
#define COMMON_H
#endif

#ifndef SONG_H
#include "song.h"
#define SONG_H
#endif

#define STACKSIZE 256
#define WORDSIZE 256



typedef struct listt
{
	char* folder;
	char* file;
	struct listt* next;
} list;



typedef struct splitlistt
{
	char* s;
	struct splitlistt* next;
	struct splitlistt* prev;
} splitlist;



typedef struct
{
	int size;
	char items[STACKSIZE][WORDSIZE];
} stack;



void printListAligned (list* l);
void printSplit (splitlist* l);
splitlist* split (char* s, char c);
void readDirectory (list** new_list, list** current_list);
splitlist** splitAll (list* l, char c, int* result_len);
void renameFiles (list** l);
void removeCommonWords (splitlist** sl, int sl_len);
list* loadFolders (char* start_dir);
