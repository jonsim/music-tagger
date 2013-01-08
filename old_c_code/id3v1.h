#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef COMMON_H
#include "common.h"
#define COMMON_H
#endif

#ifndef SONG_H
#include "song.h"
#define SONG_H
#endif

song* extractID3v1 (char* file_name);
