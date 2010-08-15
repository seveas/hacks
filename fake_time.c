/*
 * fake_time.c -- Report fake date/time
 *
 * All calls to get the current date/time on linux come down to calling
 * gettimeofday, clock_gettime, time, or ftime in the C library. This cfile
 * can be compiled into a shared library that overrides these four calls
 * via LD_PRELOAD. This way you can make your app think differently about
 * time, which is useful for testing and fuzzing.
 *
 * To compile the library:
 *
 * gcc -Wall -fPIE -shared -o fake_time.so fake_time.c
 *
 * To use the library, set the following environment variables:
 *
 * export LD_PRELOAD=/path/to/fake_time.so
 * export FAKE_TIME=1281228785
 *
 * All calls to retrieve the current time will then report the value of
 * FAKE_TIME (which is interpreted as seconds since epoch). The Default 
 * value for FAKE_TIME is 1234567890 or Fri Feb 13 23:31:30 UTC 2009
 *
 * You can also change the value that will be returned by simply calling
 * setenv from your code to update the FAKE_TIME variable.
 *
 * Beware: any processes spawned by your code will inherit the fake_time
 * behaviour unless you clean the environment variable LD_PRELOAD before
 * calling execve or one of the many wrappers around it
 *
 * (c)2010 Dennis Kaarsemaker <dennis@kaarsemaker.net> Dedicated to the 
 * public domain
 */

#include <stdlib.h>
#include <sys/time.h>
#include <sys/timeb.h>
#include <time.h>
#undef gettimeofday
#undef clock_gettime
#undef time
#undef ftime

#define DEFAULT_FAKE_TIME (1234567890)
#define FAKE_TIME_VAR "FAKE_TIME"

static long get_time() {
    int fake_time;
    char *env_time = getenv(FAKE_TIME_VAR);
    char *err = NULL;
    if(!env_time)
        return DEFAULT_FAKE_TIME;
    fake_time = strtol(env_time, &err, 10);
    if(err && *err)
        return DEFAULT_FAKE_TIME;
    return fake_time;
}

int gettimeofday(struct timeval *tv, struct timezone *tz) {
   if(tv == NULL)
        return -1;
   tv->tv_sec = get_time();
   return 0;
}

int clock_gettime(clockid_t clk_id, struct timespec *tp) {
    if(tp == NULL)
        return -1;
    tp->tv_sec = get_time();
    return 0;
}

time_t time(time_t *t) {
    int t_ = get_time();
    if(t)
        *t = t_;
    return t_;
}

int ftime(struct timeb *tp) {
    tp->time = get_time();
    return 0;
}
