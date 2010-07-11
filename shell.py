# shell.py - A pythonic version of perl's 'use Shell;'
# (c) 2010 Dennis Kaarsemaker <dennis@kaarsemaker.net>
#
# Usage:
# from shell import shell, pipe
# result = shell.cp('/tmp/foo', '/tmp/bar')
# result = pipe(pipe.ls('/home') | pipe.grep('-v', 'dennis'))
#
# * The shell object will walk your $PATH to find commands, calling the command
#   is done through subprocess, you can use subprocess keyword arguments in
#   your calls for maximum flexibility.
#
# * The pipe object defers starting the process until you chain another process
#   to it via the | operator. A wrapping call to pipe executes the last process
#   and returns all(!) returncodes and stdout/stderr
#
# Each shell.foo command accepts both regular and keyword arguments. Regular
# arguments are passed to the command as arguments, keyword arguments are
# passed to the underlying subprocess, see the subprocess documentation for
# possibilities. The constants subprocess.PIPE and subprocess.STDOUT are
# mirrored as shell.PIPE and shell.STDOUT for completeness
#
# By default, input/output will be redirected to pipes to the current program
# so it can be captured. If you do not want this (say, for running vim), either
# specify stdin/stdout/stderr to be None or give the keyword argument
# 'redirect' with a False value. If the keyword argument 'input' is given, it
# should be a string. This will be passed as input to the command via the
# communicate method. The 'input' keyword is only supported for shell, not for
# pipe. Processes in the middle of a pipe only support assignment to stderr,
# mostly so that stderr=pipe.STDOUT or stderr=open('/dev/null','w') works as
# expected.
#
# Since python does not accept '-' in an identifiers name, you can replace it
# with a '_' and make the shell find it, for example:
# shell.apt_cache('show','python')
#
# The return value of a command is a tuple (exitcode, stdout, stderr). It is a
# named tuple, so you can address those fields by name as well as by index.
# Shell commands return a single returncode, pipecommands a list of them, in
# pipe order.
#
# This script is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 3, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

try:
    from collections import namedtuple
    Result = namedtuple('Result', ('returncode','stdout','stderr'))
except ImportError:
    # namedtuple only exists in 2.6+
    class Result(tuple):
        __slots__ = ()
        def __new__(cls, returncode, stdout, stderr):
            return tuple.__new__(cls, (returncode, stdout, stderr))
        def __repr__(self):
            return 'Result' + super(Result, self).__repr__()
        returncode = property(lambda self: self[0])
        stdout = property(lambda self: self[1])
        stderr = property(lambda self: self[2])
import os
import os.path
import subprocess

__all__ = ['shell','pipe','PIPE','STDOUT']
# Mirror some subprocess constants
PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT

class Shell(object):
    """The magic shell class that finds executables on your $PATH"""
    # Mirror some module-level constants as we expect people to 'from shell
    # import shell'
    PIPE = PIPE
    STDOUT = STDOUT

    def __getattr__(self, name):
        # Real functionality factored out for subclass purposes. super()
        # instances cannot really do __getattr__
        return self._getattr(name, defer=False)

    def _getattr(self, name, defer):
        """Locate the command on the PATH"""
        try:
            return super(Shell, self).__getattribute__(name)
        except AttributeError:
            name_ = name.replace('_','-')
            for d in os.environ['PATH'].split(':'):
                p = os.path.join(d, name)
                if os.access(p, os.X_OK):
                    return Command(p,defer=defer)
                # Try a translation from _ to - as python identifiers can't
                # contain -
                p = os.path.join(d, name_)
                if os.access(p, os.X_OK):
                    return Command(p,defer=defer)
            raise

class Pipe(Shell):
    """Shell subclass that returns defered commands"""
    def __getattr__(self, name):
        """Return defered commands"""
        return self._getattr(name, defer=True)

    def __call__(self, cmd):
        """Run the last command in the pipeline and return data"""
        return cmd.run_pipe()

class Command(object):
    """A subprocess wrapper that executes the program when called or when
       combined with the or operator for pipes"""
    def __init__(self, name=None, defer=False):
        self.name = str(name)
        self.defer = defer

    def __call__(self, *args, **kwargs):
        """Save arguments, execute a subprocess unless we need to be defered"""
        self.args = args
        # When not specified, make sure stdio is coming back to us
        kwargs['close_fds'] = True
        if kwargs.pop('redirect', True):
            for stream in ('stdin', 'stdout', 'stderr'):
                if stream not in kwargs:
                    kwargs[stream] = PIPE
        self.input = kwargs.pop('input','')
        self.defer = kwargs.pop('defer', self.defer)
        self.kwargs = kwargs
        if not self.defer:
            # No need to defer, so call ourselves
            sp = subprocess.Popen([str(self.name)] +
                    [str(x) for x in self.args], **(self.kwargs))
            (out, err) = sp.communicate(self.input)
            return Result(sp.returncode, out, err)
        # When defering, return ourselves
        self.next = self.prev = None
        return self

    def __or__(self, other):
        """Chain processes together and execute a subprocess for the first
           process in the chain"""
        # Can we chain the two together?
        if not isinstance(other, self.__class__):
            raise TypeError("Can only chain commands together")
        if not self.defer or not hasattr(self, 'next') or self.next:
            raise ValueError("Command not chainable or already chained")
        if not other.defer or not hasattr(other, 'prev') or other.prev:
            raise ValueError("Command not chainable or already chained")
        if not hasattr(self, 'args') or not hasattr(other, 'args'):
            raise ValueError("Command not called yet")
        # Can't chain something with input behind something else
        if hasattr(other, 'input') and other.input != '':
            raise ValueError("Cannot chain a command with input")
        # Yes, we can!
        self.next = other
        other.prev = self
        r, w = os.pipe()
        self.kwargs['stdout'] = PIPE
        self.sp = subprocess.Popen([str(self.name)] + [str(x) for x in self.args], **(self.kwargs))
        other.kwargs['stdin'] = self.sp.stdout
        return other

    def run_pipe(self):
        """Run the last command in the pipe and collect returncodes"""
        sp = subprocess.Popen([str(self.name)] + [str(x) for x in self.args], **(self.kwargs))

        # Ugly fudging of file descriptors to make communicate() work
        old_stdin = sp.stdin
        proc = self.prev
        input = ''
        while proc:
            sp.stdin = proc.sp.stdin
            input = proc.input
            if proc.sp.stdout:
                proc.sp.stdout.close()
                proc.sp.stdout = None
            if proc.sp.stderr:
                proc.sp.stderr.close()
                proc.sp.stderr = None
            proc = proc.prev

        (out, err) = sp.communicate(input)

        sp.stdin = old_stdin

        returncodes = [sp.returncode]
        proc = self.prev
        while proc:
            returncodes.insert(0, proc.sp.wait())
            proc = proc.prev
        return Result(returncodes, out, err)

# You really only need one Shell or Pipe instance, so let's create one and recommend to
# use it.
shell = Shell()
pipe = Pipe()

# Testing is good. Must test.
if __name__ == '__main__':
    import unittest

    class ShellTest(unittest.TestCase):
        def test_notfound(self):
            # Non-existing command
            self.assertRaises(AttributeError, lambda: shell.cd)

        def test_basic(self):
            # Basic command test
            r = shell.ls('/')
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stderr, '')
            self.assertTrue(r.stdout != '')

        def test_underscores(self):
            # Underscore-replacement
            c = shell.ssh_add
            self.assertTrue('ssh-add' in c.name)
            r = c('-l')
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stderr, '')
            self.assertTrue(r.stdout != '')

        def test_pipes(self):
            # Test basic pipe usage
            r = pipe(pipe.ls('/') | pipe.grep('-v', 'bin') | pipe.rot13() | pipe.rot13())
            self.assertEqual(r.returncode, [0,0,0,0])
            self.assertTrue('bin' not in r.stdout)
            self.assertEqual(r.stderr,'')

        def test_pipe_madness(self):
            # Test broken usage
            self.assertRaises(TypeError, lambda: pipe.cat() | None)
            self.assertRaises(ValueError, lambda: pipe.cat() | shell.ls)
            self.assertRaises(ValueError, lambda: shell.ls | pipe.cat())
            self.assertRaises(ValueError, lambda: pipe.ls | pipe.cat())
            self.assertRaises(ValueError, lambda: pipe.ls() | pipe.cat)

        def test_pipe_oneprocess(self):
            # Name says all
            r = pipe(pipe.ls('/'))
            self.assertEqual(r.returncode, [0])
            self.assertEqual(r.stderr, '')
            self.assertTrue(r.stdout != '')

        def test_pipe_stderr(self):
            # Stderr redirection in the middle of the pipe
            r = pipe(pipe.echo("Hello, world!") | pipe.grep("--this-will-not-work", stderr=STDOUT) | pipe.cat())
            self.assertEqual(r.returncode[0], 0)
            self.assertTrue(r.returncode[1] > 1)
            self.assertEqual(r.returncode[2], 0)
            self.assertTrue('this-will-not-work' in r.stdout)
            self.assertEqual(r.stderr, '')

        def test_stderr(self):
            # Command with stderr
            r = shell.ls('/does/not/exist')
            self.assertTrue(r.returncode != 0)
            self.assertEqual(r.stdout, '')
            self.assertTrue(r.stderr != '')

        def test_withinput(self):
            # with inputstring
            inp = 'Hello, world!'
            r = shell.cat(input=inp)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(inp, r.stdout)
            self.assertEqual('', r.stderr)

        def test_withio(self):
            # Use open filehandles
            fd = open('/etc/resolv.conf')
            data = fd.read()
            fd.seek(0)
            r = shell.rot13(stdin=fd)
            fd.close()
            self.assertEqual(r.returncode, 0)
            self.assertEqual(data.encode('rot13'), r.stdout)
            self.assertEqual(r.stderr, '')

        def test_withoutredirect(self):
            # Run something with redirect=False
            r = shell.echo("-n",".", redirect=False)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout, None)
            self.assertEqual(r.stderr, None)

        def test_pipewithinput(self):
            input = "Hello, world!"
            r = pipe(
                pipe.caesar(10, input=input) |
                pipe.caesar(10) |
                pipe.caesar(6)
            )
            self.assertEqual(r.returncode, [0,0,0])
            self.assertEqual(r.stdout, input)
            self.assertEqual(r.stderr, '')

        def test_pipewithhugeinput(self):
            input = "123456789ABCDEF" * 1024
            r = pipe(
                pipe.caesar(10, input=input) |
                pipe.caesar(10) |
                pipe.caesar(6)
            )
            self.assertEqual(r.returncode, [0,0,0])
            self.assertEqual(r.stdout, input)
            self.assertEqual(r.stderr, '')

    unittest.main()
