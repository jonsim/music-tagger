/*-----------------------------------------------------------------------*/
/*----------------------------    LICENSE    ----------------------------*/
/*-----------------------------------------------------------------------*/
/* This file is part of the music_tagger program                         */
/* (https://github.com/jonsim/music_tagger).                             */
/*                                                                       */
/* Foobar is free software: you can redistribute it and/or modify        */
/* it under the terms of the GNU General Public License as published by  */
/* the Free Software Foundation, either version 3 of the License, or     */
/* (at your option) any later version.                                   */
/*                                                                       */
/* Foobar is distributed in the hope that it will be useful,             */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of        */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         */
/* GNU General Public License for more details.                          */
/*                                                                       */
/* You should have received a copy of the GNU General Public License     */
/* along with Foobar.  If not, see <http://www.gnu.org/licenses/>.       */
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
