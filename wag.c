/*
 * Wag: watch a file and wag your tail when it changes.
 * Usage: wag /path/to/file /path/to/executable [args for executable]
 *
 * Every time the mtime of the watched file changes, the executable is executed
 * with the arguments as given to wag.
 *
 * Do not use this if you have inotify available on your system, as inotify is
 * the proper way of watching files. I wrote this for a linux 2.4 system where
 * inotify is not available.
 *
 * (c)2009 Dennis Kaarsemaker, dedicated to the public domain.
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

void usage(char *prog, int exitcode) {
    printf("Usage: %s <filename-to-watch> <app-to-execute> [args]\n", prog);
    puts("The app will be executed whenever the file changes");
    exit(exitcode);
}

#define perror_quit(msg) do { perror(msg); exit(1); } while(0)

int main(int argc, char **argv) {
    struct stat buf;
    char *file;
    time_t last_change = 0;
    pid_t child;
    int status;

    if(argc < 3)
        usage(argv[0], 1);
    file = argv[1];
    argc -= 2;
    argv = &(argv[2]);

    if(access(file, R_OK) || access(argv[0], R_OK|X_OK))
        usage(argv[0], 2);

    while(1) {
        if(stat(file, &buf) == -1)
            perror_quit("Stat failed");

        if(buf.st_mtime != last_change) {
            last_change = buf.st_mtime;
            child = fork();
            if(child == -1)
                perror_quit("Fork failed");
            if(child == 0){
                execv(argv[0], argv);
                perror_quit("Exec failed");
            }
            waitpid(child, &status, 0);
        }
       sleep(1);
    }
}
