/* suid_script_wrapper.c
 *
 * Wrapper around scripts for chmod +s purposes. Scripts can only be setuid if
 * their interpreter is, which most interpreters are not. You can work around
 * this limitation with this program. You must hardcode the full path to both
 * interpreter and script to prevent security breaches.
 *
 * An example script is included below.
 * 
 * The first four #define's below configure the program, the rest of the code
 * should not be changed.
 *
 * You should only use this program if sudo is not available for you.

% cat /tmp/suidtest.py
import os, sys
print "UID: %d GID: %d" % (os.getuid(), os.getgid())
print "EUID: %d EGID: %d" % (os.geteuid(), os.getegid())
print "ARGV: %s" % str(sys.argv)
print "ENVP: %s" % str(os.environ)

 * (c)2008 Dennis Kaarsemaker - Dedicated to the public domain
 */

/* Full path to interpreter */
#define INTERPRETER_PATH "/usr/bin/python"
/* Full path to script */
#define SCRIPT_PATH      "/tmp/suidtest.py"
/* Pass argv on or not */
#define TAKE_ARGV        1
/* Paranoid mode: Every involved file should be owned by root */
#define PARANOID         1

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

extern char **environ;

/* Clear the environment. Only preserve USER/USERNAME/LOGNAME/HOME/LANG/LC_* */
void clear_environ() {
    char **env = environ;
    size_t len;
    char *key;
    while(*env) env++;
    do {
        env--;
        len = strchr(*env, '=') - *env;
        key = strndup(*env, len);
        /* You can extend this list if you want, but be careful */
        if(strcmp(key, "USER") &&
           strcmp(key, "USERNAME") &&
           strcmp(key, "LOGNAME") &&
           strcmp(key, "HOME") &&
           strcmp(key, "LANG") &&
           strncmp(key, "LC_", 3)
          )
            unsetenv(key);
        free(key);
    } while (env != environ);
    /* Inject a few safe things */
    setenv("PATH","/bin:/sbin:/usr/bin:/usr/sbin:/usr/games:/usr/X11/bin", 1);
    setenv("IFS"," \t\n", 1);
}

int main(int argc, char **argv) {
    int ret = 0;
    struct stat buf1, buf2;
    char *interpreter_path = INTERPRETER_PATH;
    char *script_path = SCRIPT_PATH;

    clear_environ();

    /* Config errors */
    if(strchr(interpreter_path, '/') != interpreter_path) {
        fprintf(stderr, "Path to interpreter not absolute\n");
        ret |= 1;
    }
    if(strchr(script_path, '/') != script_path) {
        fprintf(stderr, "Path to script not absolute\n");
        ret |= 1;
    }

    /* Access errors */
    if(stat(argv[0], &buf1) == -1) {
        perror("stat on argv[0] failed");
        ret |= 2;
    }
    if(!(buf1.st_mode & (S_ISGID | S_ISUID))) {
        fprintf(stderr, "Wrapper isn't suid/sgid\n");
        ret |= 2;
    }
    if(access(interpreter_path, X_OK)) {
        perror("Cannot execute interpreter " INTERPRETER_PATH);
        ret |= 2;
    }
    if(access(script_path, R_OK)) {
        perror("Cannot read script " SCRIPT_PATH);
        ret |= 2;
    }

    /* Permission/owner errors */
    if(!stat(argv[0], &buf1) && !stat(script_path, &buf2)) {
#if PARANOID
        if((buf1.st_uid != 0) || (buf1.st_gid != 0)) {
            fprintf(stderr, "%s is not owned by root\n", argv[0]);
            ret |= 4;
        }
        if((buf2.st_uid != 0) || (buf2.st_gid != 0)) {
            fprintf(stderr, "%s is not owned by root\n", script_path);
            ret |= 4;
        }
#else
        if((buf1.st_mode & S_ISGID) && (buf1.st_gid != buf2.st_gid)) {
            fprintf(stderr, "Mismatch betweeen the gid of %s and %s\n", argv[0], script_path);
            ret |= 4;
        }
        if((buf1.st_mode & S_ISUID) && (buf1.st_uid != buf2.st_uid)) {
            fprintf(stderr, "Mismatch betweeen the uid of %s and %s\n", argv[0], script_path);
            ret |= 4;
        }
#endif
        if((buf1.st_mode & S_ISGID) && (buf1.st_mode & S_IWGRP)) {
            fprintf(stderr, "%s is world writable\n", argv[0]);
            ret |= 4;
        }
        if((buf1.st_mode & S_ISGID) && (buf2.st_mode & S_IWGRP)) {
            fprintf(stderr, "%s is world writable\n", script_path);
            ret |= 4;
        }
        if((buf1.st_mode & S_ISGID) && (buf1.st_mode & (S_IWGRP | S_IWOTH))) {
            fprintf(stderr, "%s is world/group writable\n", argv[0]);
            ret |= 4;
        }
        if((buf1.st_mode & S_ISGID) && (buf2.st_mode & (S_IWGRP | S_IWOTH))) {
            fprintf(stderr, "%s is world/group writable\n", script_path);
            ret |= 4;
        }
    }

    /* Interpreter check */
    if(!stat(interpreter_path, &buf1)) {
        if(buf1.st_uid != 0) {
            fprintf(stderr, "Invalid interpreter, not owned by root\n");
            ret |= 8;
        }
        if(buf1.st_mode & (S_IWGRP | S_IWOTH)) {
            fprintf(stderr, "%s is world/group writable\n", interpreter_path);
            ret |= 8;
        }
    }

    if(ret)
        return ret | 128;

    #if TAKE_ARGV
    char **new_argv = (char**)malloc((argc+2) * sizeof(char*));
    int i = 1;
    new_argv[0] = interpreter_path;
    new_argv[1] = script_path;
    while(i < argc) {
        new_argv[i+1] = argv[i];
        i++;
    }
    new_argv[i+1] = NULL;
    #else
    char* new_argv[3] = {interpreter_path, script_path, NULL};
    #endif

    execve(interpreter_path, new_argv, environ);
    perror("Could not execute wrapped script " INTERPRETER_PATH " " SCRIPT_PATH);
    return 16 | 128;
}
