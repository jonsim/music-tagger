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


/*-----------------------------------------------------------------------*/
/*---------------------------    INCLUDES    ----------------------------*/
/*-----------------------------------------------------------------------*/
#include "renamer.h"




/*-----------------------------------------------------------------------*/
/*------------------------    LIST FUNCTIONS    -------------------------*/
/*-----------------------------------------------------------------------*/
/* adds an element to a list, copying the contents of the char* passed to it,
   returning a pointer to the new head*/
list* addList (list* existing, char* folder_insert, char* file_insert)
{
	list *new = malloc(sizeof(list));
	char folder_len = strlen(folder_insert);
	char file_len = strlen(file_insert);
	
	new->folder = calloc(folder_len, sizeof(char));
	new->file = calloc(file_len, sizeof(char));
	memcpy(new->folder, folder_insert, folder_len + 1);
	memcpy(new->file, file_insert, file_len + 1);
	
	new->next = existing;

	return new;
}


/* prints the elements in a list, aligned by the longest folder name */
int printListAlignedR (list* l, int max)
{
	int i;
	int folder_len = strlen(l->folder);
	int new_max = (folder_len > max) ? folder_len : max;
	
	if (l->next != NULL)
		new_max = printListAlignedR(l->next, new_max);
	
	printf("[%s]", l->folder);
	for (i = 0; i < new_max - folder_len; i++)
		putchar(' ');
	printf(" %s\n", l->file);
	
	
	return new_max;
}


/* calls the recursive version of the function (above) */
void printListAligned (list* l)
{
	printListAlignedR (l, 0);
}


/* prints the elements in a list */
void printList (list* l)
{
	if (l->next != NULL)
		printList(l->next);
	printf("[%s] %s\n", l->folder, l->file);
}




/*-----------------------------------------------------------------------*/
/*----------------------    SPLITLIST FUNCTIONS    ----------------------*/
/*-----------------------------------------------------------------------*/
/* adds a new element (char*) to a splitlist (which is doubly linked), returning
   a pointer to the new head */
splitlist* addSplit (splitlist* existing, char* to_insert)
{
	splitlist* new = malloc(sizeof(splitlist));

	new->s = to_insert;
	new->next = existing;
	new->prev = NULL;
	if (existing != NULL)
		existing->prev = new;

	return new;
}


/* removes an element from a splitlist (which is double linked), returning a
   pointer to the next element after the removed one in the splitlist */
splitlist* removeSplit (splitlist* to_remove)
{
	if (to_remove == NULL)
		return NULL;
	splitlist* nextp = to_remove->next;
	splitlist* prevp = to_remove->prev;
	
	if (nextp != NULL)
		nextp->prev = prevp;
	if (prevp != NULL)
		prevp->next = nextp;
	free(to_remove);
	return nextp;
}


/* rewinds a splitlist to the first element (this is the reason the splitlist is
   doubly linked)  */
splitlist* rewindSplit (splitlist* l)
{
	if (l == NULL)
		return NULL;
	while (l->prev != NULL)
		l = l->prev;
	return l;
}


/* prints the elements in a splitlist */
void printSplit (splitlist* l)
{
	if (l->next != NULL)
		printSplit(l->next);
	printf("%s, ", l->s);
}


/* copies splitlist current into splitlist new */
void splitCopy (splitlist** new, splitlist* current)
{
	if (current->next != NULL)
		splitCopy (new, current->next);
	*new = addSplit(*new, current->s);
}


/* splits a string given on character c, returning a splitlist of elements */
splitlist* split (char* s, char c)
{
	char* new_split;
	splitlist* result = NULL;
	
	char* head = s;
	char* tail = s;
	
	while (*head != '\0')
	{
		if (*head == c)
		{
			if (head > tail)
			{
				new_split = calloc(head - tail + 1, sizeof(char));
				memcpy(new_split, tail, head - tail);
				new_split[head - tail] = '\0';
				
				result = addSplit(result, new_split);				
			}
			tail = ++head;
		}
		else
			head++;
	}
	
	new_split = calloc(head - tail + 1, sizeof(char));
	memcpy(new_split, tail, head - tail);
	new_split[head - tail] = '\0';
	
	result = addSplit(result, new_split);	
	
	return result;
}


/* splits a list of strings on character c, returning an array of splitlists.
   the length of the array returned is saved into result_len */
splitlist** splitAll (list* l, char c, int* result_len)
{
	int i, files;
	list* l_start = l;
	splitlist** result;
	
	/* count the number of files passed in and allocate enough space for them */
	if (l == NULL)
		return NULL;
	for (files = 1; l->next != NULL; files++)
		l = l->next;
	l = l_start;
	result = calloc(files, sizeof(splitlist*));
	
	/* split the filename of each element and store it in the new array */
	for (i = 0; i < files; i++)
	{
		result[i] = split(l->file, c);
		l = l->next;
	}
	
	if (result_len != NULL)
		*result_len = files;
	return result;
}




/*-----------------------------------------------------------------------*/
/*------------------------    STACK FUNCTIONS    ------------------------*/
/*-----------------------------------------------------------------------*/
/* pushes an item onto the stack, forming it by concatenating char arrays x and
   y together with a '/' between them (i.e. building a file path) */
void push (stack* s, char* x, char* y)
{
	int ss = s->size;
	
	if (ss == STACKSIZE)
		fputs("Error: external stack overflow.\n", stderr);
	else
		if (x != NULL)
		{
			strcpy(s->items[ss], x);
			s->items[ss][strlen(x)] = '/';
			s->items[ss][strlen(x)+1] = '\0';
			strcat(s->items[ss], y);
		}
		else
		{
			strcpy(s->items[ss], y);
		}
		s->size++;
}


/* pops an item off the stack, modifying the stack* given to reflect the pop,
   and returning the element popped off */
char* pop (stack* s)
{
	if (s->size == 0)
	{
		fputs("Error: external stack underflow.\n", stderr);
		return NULL;
	}
	return s->items[--s->size];
}





/*-----------------------------------------------------------------------*/
/*-----------------------    PROGRAM FUNCTIONS    -----------------------*/
/*-----------------------------------------------------------------------*/
/* description */
list* loadFolders (char* start_dir)
{
	DIR* dp;
	struct dirent* ep;
	stack* folders_to_visit = malloc(sizeof(stack));
	list* result = NULL;
	char current_dir[WORDSIZE];
	
	push(folders_to_visit, NULL, start_dir);
	
	// fill the list with files and folders, by navigating the directory
	// structure from the start folder up. keep opening folders and finding
	// files until no more are found 
	while (folders_to_visit->size != 0)
	{
		// pop a folder to visit off the stack and open it
		strcpy(current_dir, pop(folders_to_visit));
		dp = opendir(current_dir);
		
		// if the directory popped exists read from it, otherwise error and exit
		if (dp != NULL)
		{
			while ((ep = readdir(dp)))
				// ignore hidden folders
				if (ep->d_name[0] != '.')
				{
					// if a folder is found, push it to the stack to visit
					if (ep->d_type == 4)
						push(folders_to_visit, current_dir, ep->d_name);
					// if a file is found add it to the list
					else
						result = addList(result, current_dir, ep->d_name);
				}
			(void) closedir(dp);
		}
		else
		{
			printf("Could not open directory '%s'\n", current_dir);
			return NULL;
		}
	
	}
	return result;
}


/* description */
void readDirectory (list** new_list, list** current_list)
{
	char* folder = (*current_list)->folder;
	list* current_list_start = NULL;

	if (*current_list == NULL)
		return;
	if (*new_list != NULL)
		free(new_list);
	*new_list = malloc(sizeof(list*));
	*new_list = *current_list;
	
	/* if there is a next list element and it's in the same folder, go to it */
	while ((*current_list)->next != NULL && strcmp((*current_list)->next->folder, folder) == 0)
		*current_list = (*current_list)->next;
	
	current_list_start = (*current_list)->next;
	(*current_list)->next = NULL;
	*current_list = current_list_start;
}


/* for all words in the list, replace the last '.', all '_' and '-' with spaces,
   then remove duplicate spaces before finally fixing the capitalisation */
void renameFiles (list** l)
{
	list* l_start = *l;
	
	while ((*l) != NULL)
	{
		replaceCharacter((*l)->file, '.', 1);
		replaceCharacter((*l)->file, '_', 0);
		replaceCharacter((*l)->file, '-', 0);
		removeDuplicateSpaces((*l)->file);
		fixCapitals((*l)->file);
		
		*l = (*l)->next;
	}
	
	*l = l_start;
}


/* description */
void removeCommonWords (splitlist** sl, int sl_len)
{
	int i, matched, to_match_len = 0;
	splitlist* to_match = NULL;
	
	splitCopy(&to_match, sl[0]);
	
	/* count the number of matches to be made */
	for (; to_match != NULL; to_match = to_match->next)
		to_match_len++;
	to_match = rewindSplit(to_match);
	
	/* match each split in each splitlist string against the list of matches
	   generated previously. after completion to_match_len indicates the number
	   of common words found. */
	for (i = 1; i < sl_len; i++)
	{
		do
		{
			
		} while (to_match->next != NULL);
	
	
		while (to_match != NULL)
		{
			matched = 0;
			while (sl[i] != NULL)
			{
				if (strcmp(to_match->s, sl[i]->s) == 0)
				{
					matched = 1;
					break;
				}
				
				sl[i] = sl[i]->next;
			}
			
			if (!matched)
			{
				to_match = removeSplit(to_match);
				to_match_len--;
			}
			else
				to_match = to_match->next;
			sl[i] = rewindSplit(sl[i]);
		}
	}
	printf("to_match_len = %d\n", to_match_len);
	to_match = rewindSplit(to_match);
	if (to_match == NULL)
		printf("problem\n");
	printSplit(to_match);
	printf("\n");
	to_match = rewindSplit(to_match);
	
	/* if any matches were found, remove them from s */
	if (to_match_len > 0)
	{
		printf("removing\n");
		while (to_match != NULL)
		{
			for (i = 0; i < sl_len; i++)
			{
				while (sl[i] != NULL)
				{
					if (strcmp(to_match->s, sl[i]->s) == 0)
						sl[i] = removeSplit(sl[i]);
					else
						sl[i] = sl[i]->next;
				}
				sl[i] = rewindSplit(sl[i]);
			}
			
			to_match = to_match->next;
		}
	}
}




/*-----------------------------------------------------------------------*/
/*-------------------------    MAIN FUNCTION    -------------------------*/
/*-----------------------------------------------------------------------*/
/* not entirely sure what this is doing here, looks like a remnant of some
   unit testing. can probably be safetly removed. */
/*  if (test)
	{
		printf("\nRunning renamer on the folder '%s' would produce the following output.\nCheck this is sane and use the -f argument to apply the changes:\n\n", start_dir);
		if (aligned)
			printListAligned(fl);
		else
			printList(fl);
		printf("\n");
	}*/
