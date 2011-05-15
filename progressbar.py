# Abuse the power of unicode to give smooth progressbars in the terminal
#
# Unicode defines the codepoints 0x2588 up to 0x258F as SOLID BLOCK, LEFT SEVEN
# EIGHTS BLOCK etc.. This can be used for almost pixel-by-pixel painting of a
# progressbar. The Progressbar class does that for you and can also guess what
# width your progressbar should be.
#
# Usage:
# Progressbar(target=100, start=0, reserve=20, columns=None)
#  - target is the final numerical goal of the progressbar
#  - start is the progress set at the beginning
#  - reserve is the amount of space to reserve for text to the right of the
#    progressbar for extra information
#  - columns is the total width of progressbar and text. This can usually be
#    autodetected, so you can omit this parameter
#
# Progressbars have one function:
#
# Progressbar.set_progress(progress, text="%(progress)s/%(target)s", args=None):
#
# - progress is the numerical progress towards the target.
# - text is the status text that goes to the right of the bar
# - args is a dict of variables that the text needs. The variables progress and
#   target are filled in automatically
#
# When the progress is equal to, or higher than the target. The progressbar is
# finalized. A final newline is printed and further calls to set_progress are
# ignored. Until the progressbar is complete, progress can go backwards if you
# want to. See the bottom of this file for a demonstration.
#
# The following attributes can be read, but should not be changed directly:
#
# - Progressbar.columns  -- What the progressbar thinks the wodth of your terminal is
# - Progressbar.target   -- The target of the progressbar
# - Progressbar.progress -- The progress towards that target
# - Progressbar.complete -- Whether the target has been reached

from __future__ import division
import fcntl 
import termios
import os
import struct
import sys

class Progressbar(object):
    chars = [x.encode('utf-8') for x in u' \u258f\u258e\u258d\u258c\u258b\u258a\u2589\u2588']
    def __init__(self, target=100, start=0, reserve=20, columns=None):
        self.reserve = reserve
        if columns:
            self.columns = columns
        elif 'COLUMNS' in os.environ:
            self.columns = os.environ['COLUMNS']
        else:
            try:
                _, self.columns = struct.unpack('hh', fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, '1234'))
            except:
                self.columns = 80

        self.columns -= reserve
        if self.columns < 10:
            raise ValueError("Screen too small for a progressbar")

        self.target = target
        self.complete = False
        self.psl = 0
        self.set_progress(start)

    def set_progress(self, progress, text="%(progress)s/%(target)s", args=None):
        if self.complete:
            return
        self.progress = progress
        if progress >= self.target:
            self.progress = self.target
            self.complete = True

        full = self.progress / self.target * self.columns
        args_ = {'progress': self.progress, 'target': self.target}
        if args:
            args_.update(args)
        bar = "\r%s%s%s%s%s" % ( self.chars[-1] * int(full),
                ('' if self.complete else self.chars[int((full-int(full)) * 8)]),
                self.chars[0] * (self.columns - int(full) -1),
                self.chars[1],
                text % args_
        )
        psl = len(bar)
        bar += ' ' * max(0,self.psl-len(bar))
        bar += '\b' * max(0,self.psl-len(bar))
        self.psl = psl
        sys.stdout.write(bar)
        if self.complete:
            sys.stdout.write('\n')
        sys.stdout.flush()

if __name__ == '__main__':
    # Demonstration 
    import time
    step = 0.1
    target = 111

    pb = Progressbar(target=target, reserve=30)
    while not pb.complete:
        pb.set_progress(pb.progress + step, 
                        "%(progress)s/%(target)s (Demo 1)")
        time.sleep(0.02)

    pb = Progressbar(target=target, reserve=30)
    while pb.progress < target * 0.8:
        pb.set_progress(pb.progress + step, 
                        "%(progress)s/%(target)s (Demo 2)")
        time.sleep(0.02)
    while pb.progress > target * 0.3:
        pb.set_progress(pb.progress - step, 
                        "%(progress)s/%(target)s (Demo 2)")
        time.sleep(0.02)
    while not pb.complete:
        pb.set_progress(pb.progress + step, 
                        "%(progress)s/%(target)s (Demo 2)")
        time.sleep(0.02)
