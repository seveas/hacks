# shell.py - A pythonic version of perl's 'use Shell;'
# (c) 2010 Dennis Kaarsemaker <dennis@kaarsemaker.net>
# Released into the public domain
#
# Usage:
# from shell import shell
# (exitcode, stdout, stderr) = shell.cp('/tmp/foo', '/tmp/bar')
#
# The shell object will walk your $PATH to find commands, calling the command
# is done through subprocess, you can use subprocess keyword arguments in your
# calls for maximum flexibility. 
#
# By default, input/output will be redirected to pipes to the current program
# so it can be captured. If you do not want this (say, for running vim), either
# specify stdin/stdout/stderr to be None or give the keyword argument
# 'redirect' with a False value. If the keyword argument 'input' is given, it
# should be a string. This will be passed as input to the command via the
# communicate method. 
#
# Since python does not accept '-' in an identifiers name, you can replace it
# with a '_' and make the shell find it, for example:
# shell.apt_cache('show','python')

import collections
import os
import os.path
import subprocess

__all__ = ['shell']

class Shell(object):
    """The magic shell class that finds executables on your $PATH"""
    def __getattr__(self, name):
        """Of course it's not magic at all. It's python!"""
        try:
            return super(Shell, self).__getattribute__(name)
        except AttributeError:
            for p in os.environ['PATH'].split(':'):
                p = os.path.join(p, name)
                if os.access(p, os.X_OK):
                    return Command(p)
            name = name.replace('_','-')
            for p in os.environ['PATH'].split(':'):
                p = os.path.join(p, name)
                if os.access(p, os.X_OK):
                    return Command(p)
            raise

Result = collections.namedtuple('Result', ('exitcode','stdout','stderr'))
class Command(object):
    """A tiny subprocess wrapper that executes the program when called"""
    def __init__(self, name=None):
        self.name = name

    def __call__(self, *args, **kwargs):
        """Execute the program via subprocess, return (exitcode, stdout, stderr)"""
        # When not specified, make sure stdio is coming back to us
        if kwargs.pop('redirect', True):
            for stream in ('stdin', 'stdout', 'stderr'):
                if stream not in kwargs:
                    kwargs[stream] = subprocess.PIPE
        input = kwargs.pop('input','')
        # And go! 
        sp = subprocess.Popen([str(self.name)] + [str(x) for x in args], **kwargs)
        (out, err) = sp.communicate(input)
        return Result(sp.returncode, out, err)

# You really only need one Shell instance, so let's create one and recommend to
# use it.
shell = Shell()
