#include <string.h>
#include <stdlib.h>
#include <stdio.h>


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
