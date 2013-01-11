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
#include <string.h>
#include <stdlib.h>
#include <stdio.h>




/*-----------------------------------------------------------------------*/
/*---------------------    FUNCTION DEFINITIONS    ----------------------*/
/*-----------------------------------------------------------------------*/
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


void replaceCharacter (char* s, char c, char remove_all_but_last_character)
{
	int i, count = 0;
	
	if (remove_all_but_last_character)
	{
		for (i = 0; i < strlen(s); i++)
			if (s[i] == '.')
				count++;
		for (i = 0; i < strlen(s) && count > 1; i++)
			if (s[i] == '.')
			{
				s[i] = ' ';
				count--;
			}
	}
	else
	{
		for (i = 0; i < strlen(s); i++)
			if (s[i] == c)
				s[i] = ' ';
	}
}


void removeDuplicateSpaces (char* s)
{
	int i, j, spaces = 0;
	
	for (i = 0; i < strlen(s); i++)
		if (s[i] == ' ')
			spaces++;
		else if (spaces > 0)
		{
			if (spaces > 1)
			{
				for (j = i; j < strlen(s) + 1; j++)
					s[j - spaces + 1] = s[j];
				i -= spaces - 1;
			}
			spaces = 0;
		}
		
}


void fixCapitals (char* s)
{
	int i, new_word = 1;
	
	for (i = 0; i < strlen(s); i++)
		if (s[i] == ' ')
			new_word = 1;
		else if (new_word)
		{
			if (s[i] >= 'a' && s[i] <= 'z')
				s[i] += 'A' - 'a';
			new_word = 0;
		}
		else
			if (s[i] >= 'A' && s[i] <= 'Z')
				s[i] += 'a' - 'A';
}
