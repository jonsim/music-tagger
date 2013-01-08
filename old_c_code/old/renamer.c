#include <stdio.h>
#include <stdlib.h>
//#include <ctype.h>
#include <string.h>
#include <sys/types.h>
#include <dirent.h>

#define STACKSIZE 256
#define WORDSIZE 256

int CURRENT_FOLDER_SIZE = -1;



/*////////// TYPE DEFINITIONS //////////*/

typedef struct listt
{
	char folder[WORDSIZE];
	char file[WORDSIZE];
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



/*////////// LIST FUNCTIONS //////////*/

list* addList (list* existing, char* folder_insert, char* file_insert)
{
	list *new = malloc(sizeof(list));

	strcpy(new->folder, folder_insert);
	strcpy(new->file, file_insert);
	new->next = existing;

	return new;
}



int printListAlignedR (list* l, int max)
{
	int i, new_max = (strlen(l->folder) > max) ? strlen(l->folder) : max;
	
	if (l->next != NULL)
		new_max = printListAlignedR(l->next, new_max);
	
	printf("[%s]", l->folder);
	for (i = 0; i < new_max - strlen(l->folder); i++)
		printf(" ");
	printf(" %s\n", l->file);
	
	
	return new_max;
}



void printListAligned (list* l)
{
	printListAlignedR (l, 0);
}



void printList (list* l)
{
	if (l->next != NULL)
		printList(l->next);
	printf("[%s] %s\n", l->folder, l->file);
}



splitlist* addSplit (splitlist* existing, char* to_insert)
{
	splitlist *new = malloc(sizeof(splitlist));

	new->s = to_insert;
	new->next = existing;
	new->prev = NULL;
	if (existing != NULL)
		existing->prev = new;

	return new;
}



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



splitlist* rewindSplit (splitlist* l)
{
	if (l == NULL)
		return NULL;
	while (l->prev != NULL)
		l = l->prev;
	return l;
}



void printSplits (splitlist* l)
{
	if (l->next != NULL)
		printSplits(l->next);
	printf("%s, ", l->s);
}



/*////////// STACK FUNCTIONS //////////*/

void push (stack* s, char* x, char* y)
{
	if (s->size == STACKSIZE)
		fputs("Error: external stack overflow.\n", stderr);
	else
		if (x != NULL)
		{
			strcpy(s->items[s->size], x);
			s->items[s->size][strlen(x)] = '/';
			s->items[s->size][strlen(x)+1] = '\0';
			strcat(s->items[s->size], y);
		}
		else
		{
			strcpy(s->items[s->size], y);
		}
		s->size++;
}



char* pop (stack* s)
{
	if (s->size == 0)
	{
		fputs("Error: external stack underflow.\n", stderr);
		return NULL;
	}
	else
	{
		return s->items[--s->size];
	}
}



/*////////// PROGRAM FUNCTIONS //////////*/

splitlist* split (char* s, char c)
{
	int i, j, head = 0, tail = 0;
	splitlist* result = NULL;
	
	// iterate through the string
	for (i = 0; i < strlen(s); i++)
	{
		// if the current character is the split character
		if (s[i] == c)
		{
			// if there is a string stored, save it
			if (head > tail)
			{
				// allocate a new space for a string
				char* new_split = calloc(head - tail + 1, sizeof(char));
				for (j = 0; j < (head - tail); j++)
					new_split[j] = s[j + tail];
				new_split[j] = '\0';
				
				result = addSplit(result, new_split);
			}
			tail = ++head;
		}
		else
		{
			head++;
		}
	}
	
	// allocate a new space for a string
	char* new_split = calloc(head - tail + 1, sizeof(char));
	for (j = 0; j < (head - tail); j++)
		new_split[j] = s[j + tail];
	new_split[j] = '\0';
	result = addSplit(result, new_split);	
	
	return result;
}



char** removeOneFolder (list** fl)
{
	if (fl == NULL)
		return NULL;
	char* folder = (*fl)->folder;
	char** result = NULL;
	char** old;
	int i, words = 0;
	
	while ((*fl) != NULL)
	{
		if (strcmp(folder, (*fl)->folder) == 0)
		{
			// allocate a new space for a string
			if (words > 0)
			{
				old = result;
			}
			result = calloc(words + 1, sizeof(char*));
			if (words > 0)
			{
				for (i = 0; i < words; i++)
					result[i] = old[i];
				free(old);
			}
			
			//insert the new string
			result[words++] = (*fl)->file;
		}
		else
		{
			break;
		}
		
		(*fl) = (*fl)->next;
	}
	
	CURRENT_FOLDER_SIZE = words;
	return result;
}



void removeCommonWords (char** s)
{
	int i, matched = 0;
	splitlist* to_match;
	splitlist* current_string;
	
	if (CURRENT_FOLDER_SIZE < 1)
	{
		printf("Warning: removeCommonWords called with array size %d.\n", CURRENT_FOLDER_SIZE);
		return;
	}
	else if (CURRENT_FOLDER_SIZE == 1)
		return;
	
	// get a list of matches from the first string
	to_match = split(s[0], ' ');
	
	// try and match them with subsequent strings
	for (i = 1; i < CURRENT_FOLDER_SIZE; i++)
	{
		current_string = split(s[i], ' ');
		
		while (to_match != NULL)
		{
			while (current_string != NULL)
			{
				if (strcmp(to_match->s, current_string->s) == 0)
				{
					matched = 1;
					break;
				}
				
				current_string = current_string->next;
			}
			
			if (!matched)
				to_match = removeSplit(to_match);
			else
				to_match = to_match->next;
			current_string = rewindSplit(current_string);
		}
	}
	to_match = rewindSplit(to_match);
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



/*////////// MAIN FUNCTION //////////*/

int main (int argc, char **argv)
{
	int i;
	char test = 1, aligned = 1;
	char* start_dir = ".";
	char current_dir[WORDSIZE];
	list* fl = NULL;
	list* fl_head = NULL;
	stack* folders_to_visit = malloc(sizeof(stack));
	DIR* dp;
	struct dirent* ep;
	
	// get the start folder and push it to the stack
	for (i = 1; i < argc; i++)
		if (strcmp(argv[i], "-f") == 0)
			test = 0;
		else if (strcmp(argv[i], "-a") == 0)
			aligned = 0;
		else
		{
			if (argv[i][strlen(argv[i]) - 1] == '/')
				argv[i][strlen(argv[i]) - 1] = '\0';
			start_dir = argv[i];
		}
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
				if (ep->d_name[0] != '.')
				{
					// if a folder is found, push it to the stack to visit
					if (ep->d_type == 4)
						push(folders_to_visit, current_dir, ep->d_name);
					// if a file is found add it to the list
					else
						fl = addList(fl, current_dir, ep->d_name);
				}
			(void) closedir(dp);
		}
		else
		{
			printf("Could not open directory '%s'\n", current_dir);
			return 1;
		}
		
	}
	
	
	fl_head = fl;
	char** current_folder;
	while (fl != NULL)
	{
		// remove an entire folder full of files from the file list
		current_folder = removeOneFolder(&fl);
	
		// for all files, replace all but the last '.' with ' '
		for (i = 0; i < CURRENT_FOLDER_SIZE; i++)
			replaceCharacter(current_folder[i], '.', 1);
		
		// for all files replace all '_' with ' '
		for (i = 0; i < CURRENT_FOLDER_SIZE; i++)
			replaceCharacter(current_folder[i], '_', 0);
		
		// for all files replace all '-' with ' '
		for (i = 0; i < CURRENT_FOLDER_SIZE; i++)
			replaceCharacter(current_folder[i], '-', 0);
		
		// for all files remove duplicate spaaces
		for (i = 0; i < CURRENT_FOLDER_SIZE; i++)
			removeDuplicateSpaces(current_folder[i]);
		
		// for all files capitalise the first letter of every word
		for (i = 0; i < CURRENT_FOLDER_SIZE; i++)
			fixCapitals(current_folder[i]);
		
		// apply the removeCommonWords algorithm to remove shared words from all
		// files in the same folder
		removeCommonWords(current_folder);
	}
	fl = fl_head;
	
	if (test)
	{
		printf("\nRunning renamer on the folder '%s' would produce the following output.\nCheck this is sane and use the -f argument to apply the changes:\n\n", start_dir);
		if (aligned)
			printListAligned(fl);
		else
			printList(fl);
		printf("\n");
	}
	
	return 0;
}

