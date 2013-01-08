CC=gcc -Wall

organize: organize.c common.o id3v1.o id3v2.o renamer.o
	$(CC) organize.c common.o id3v1.o id3v2.o renamer.o -o organize

common.o: common.c
	$(CC) -c common.c -o common.o

id3v1.o: id3v1.c
	$(CC) -c id3v1.c -o id3v1.o

id3v2.o: id3v2.c
	$(CC) -c id3v2.c -o id3v2.o

renamer.o: renamer.c
	$(CC) -c renamer.c -o renamer.o

clean:
	rm -f *.o organize
