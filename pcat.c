/* pcat - cat for pipes
 *
 * The 'cat' application is not suitable for pipes as the read side of a pipe
 * gets closed when there are no more writers. pcat is a very simple cat-like
 * application that keeps the pipe open for writing too, thus ensuring that the
 * reading end doesn't get closed.
 *
 * Compiling is simple: cc -o pcat pcat.c
 *
 * (c) Dennis Kaarsemaker, released into the public domain.
 */

#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    struct stat sbuf;
    int fd1, fd2;
    char buf;
    
    if(argc != 2) {
        fprintf(stderr, "Usage: %s name-of-pipe\n", argv[0]);
        return 1;
    }
    if(stat(argv[1], &sbuf)){
        perror("stat failed");
        return 1;
    }
    if(!S_ISFIFO(sbuf.st_mode)) {
        fprintf(stderr, "%s is not a fifo", argv[1]);
        return 1;
    }
    fd1 = open(argv[1], O_WRONLY);
    fd2 = open(argv[1], O_RDONLY);
    while(read(fd2, &buf, 1)) {
        putchar(buf);
    }
    return 0;
}
