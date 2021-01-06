# Stupid ansi color demo program 'cause I keep forgetting them
# And it's reusable as a library too. Whaddayaknow.

import binascii
import os

# ANSI sexences start with ESC + [, this is called the control sequence initiator
esc = '\033'
csi = esc + '['
osc = esc + ']'
bell = bel = '\a'

# Colors and text effects are csi + code [; code]* + m. Encode these as easily
# memorable names
class Attr(object):
    def __init__(self, **attr):
        self.attr = attr
        self.rev_attr = dict([(v,k) for k,v in attr.items()])
        for k, v in attr.items():
            setattr(self, k, v)

    def __getitem__(self, item):
        return self.attr[item]

    def __iter__(self):
        for item in self.attr:
            yield item

    def name(self, val):
        return self.rev_attr[val]

class Color(Attr):
    # Xterm colors are the control sequence 38;5;<color> or 48;5;<color>
    def xterm(self, val):
        return '%d;5;%d' % (self._xterm, val)

class Cursor(Attr):
    def __init__(self, **attr):
        self.attr = attr
        self.rev_attr = dict([(v,k) for k,v in attr.items()])
        for k, v in attr.items():
            setattr(self, k, CursorItem(v))

# Normal foreground/background colors
fgcolor    = Color(black=30,  red=31,  green=32,  yellow=33,  blue=34,  magenta=35,  cyan=36,  white=37,  _xterm=38, default=39,  none=None)
bgcolor    = Color(black=40,  red=41,  green=42,  yellow=43,  blue=44,  magenta=45,  cyan=46,  white=47,  _xterm=48, default=49,  none=None)
# High intensity colors
fgcolor_hi = Color(black=90,  red=91,  green=92,  yellow=93,  blue=94,  magenta=95,  cyan=96,  white=97,             default=99,  none=None)
bgcolor_hi = Color(black=100, red=101, green=102, yellow=103, blue=104, magenta=105, cyan=106, white=107,            default=109, none=None)
# Text effects
attr       = Attr(normal=0, bright=1, faint=2, underline=4, negative=7, conceal=8, crossed=9, none=None)
# Blinking
blink      = Attr(off=25, slow=5, fast=6)

# And convenience functions to wrap text in effects. Example:
# wrap("Your text", fgcolor.red, attr.bright)
mode = lambda *args: "%s%sm" % (csi, ';'.join([str(x) for x in args if x is not None]))
reset = mode(attr.normal)
wrap = lambda text, *args: "%s%s%s" % (mode(*args), text, reset)

# The codes for manipulating the cursor accept an optional argument that
# specifies the lenght of the action:
# csi + A = move up
# csi + 4 + A = move up 4 positions
# These objects make cursor.up and cursor.up(4) work
class CursorItem(object):
    def __init__(self, key):   self.key = key 
    def __str__(self):         return csi + self.key 
    def __repr__(self):        return csi + self.key 
    def __call__(self, *val):  return csi + ';'.join([str(x) for x in val]) + self.key 
    def __add__(self, other):  return str(self) + str(other) 
    def __radd__(self, other): return str(other) + str(self) 

# The argument to erase_{line,display} specifies what to erase
class Eraser(CursorItem):
    def __call__(self, val):
        val = {'start': 1, 'end': 0, 'all': 2}.get(val, val)
        return super(Eraser, self).__call__(val)

cursor = Cursor(save='s', restore='u', up='A', down='B', forward='C', back='D',
                next_line='E', previous_line='F', column='G', position='H',
                hide='?25l', show='?25h')
erase_line = Eraser('K')
erase_display = Eraser('J')

def iterm_anchor(url, text):
    return osc + '8;;' + url + bel + text + osc + '8;;' + bel

def iterm_notification(msg):
    return osc + '9;' + msg + bel

def _b64(data):
    if not isinstance(data, bytes):
        data = data.encode()
    return binascii.b2a_base64(data, newline=False).decode()

is_iterm = os.environ['TERM_PROGRAM'] == "iTerm.app"
def iterm_badge(badge):
    return osc + '1337;SetBadgeFormat=' + _b64(badge) + bel

def iterm_image(imgdata, name="unnamed", inline=True, height=None, width=None, preserve_aspect_ratio=True, size=None):
    ret = osc + '1337;File=name=' + _b64(name)
    if inline:
        ret += ';inline=1'
    if not preserve_aspect_ratio:
        ret += ';preserveAspectRatio=0'
    if size:
        ret += ';size=%d' % size
    if width:
        ret += ';width=%s' % str(width)
    if height:
        ret += ';height=%s' % str(height)
    return ret + ':' + _b64(imgdata) + bel

def demo_colors():
    print(wrap("Standard color palette", attr.bright, attr.underline))
    for color in fgcolor:
        if color in ('none', '_xterm', 'default'):
            continue
        print("%-10s %s %s %s %s" % (color, wrap("XXX", fgcolor[color]), wrap("   ",  bgcolor[color]),
              wrap("XXX", fgcolor_hi[color]), wrap("   ", bgcolor_hi[color])))

    print("\n" + wrap("Combinations", attr.bright, attr.underline))
    for (text, dattr) in [('normal', 'none'), ('bright', 'bright'), ('faint', 'faint')]:
        for dfgcolor in fgcolor:
            if dfgcolor in ('none', '_xterm', 'default'):
                continue
            for dbgcolor in bgcolor:
                if dbgcolor in ('none', '_xterm', 'default'):
                    continue
                sys.stdout.write(wrap( " %7s " % (text), fgcolor[dfgcolor], bgcolor[dbgcolor], attr[dattr]))
            print("")

    print("\n" + wrap("xterm color palette", attr.bright, attr.underline))
#   0x00-0x07:  standard colors (as in ESC [ 30..37 m)
#   0x08-0x0f:  high intensity colors (as in ESC [ 90..97 m)
#   0x10-0xe7:  6*6*6=216 colors: 16 + 36*r + 6*g + b (0 LTE r,g,b LTE 5)
#   0xe8-0xff:  grayscale from black to white in 24 steps
    sys.stdout.write("Standard       ")
    for i in range(8):
        sys.stdout.write(wrap("%-3d" % i, fgcolor.xterm(i)))
    sys.stdout.write("\n               ")
    for i in range(8):
        sys.stdout.write(wrap("   ", bgcolor.xterm(i)))
    sys.stdout.write("\nHigh intensity ")
    for i in range(8,16):
        sys.stdout.write(wrap("%-3d" % i, fgcolor.xterm(i)))
    sys.stdout.write("\n               ")
    for i in range(8,16):
        sys.stdout.write(wrap("   ", bgcolor.xterm(i)))
    sys.stdout.write("\n216 colors     ")
    for r in range(6):
        if r:
            sys.stdout.write("\n               ")
        for c in range(36):
            x = 16+36*r+c
            sys.stdout.write(wrap("%-3d" % x, fgcolor.xterm(x)))
        sys.stdout.write("\n               ")
        for c in range(36):
            x = 16+36*r+c
            sys.stdout.write(wrap("   ", bgcolor.xterm(x)))
    sys.stdout.write("\nGrayscale      ")
    for i in range(232,256):
        sys.stdout.write(wrap("%-3d" % i, fgcolor.xterm(i)))
    sys.stdout.write("\n               ")
    for i in range(232,256):
        sys.stdout.write(wrap("   ", bgcolor.xterm(i)))

    print("\n\n" + wrap("Effects", attr.bright, attr.underline))
    for effect in attr:
        print("%-10s %s" % (effect, wrap(effect, attr[effect])))

def demo_cursor():
    print(erase_display('all'))
    height, width = struct.unpack('hh', fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, '1234'))
    matrix = [(x,y) for x in range(2,width) for y in range(2,height-1)]
    count = len(matrix)
    random.shuffle(matrix)
    arrows = b'\xe2\xac\x85\xe2\xac\x86\xe2\xac\x87\xe2\xac\x88\xe2\xac\x89\xe2\xac\x8a\xe2\xac\x8b'.decode('utf-8')
    for (current, (x, y)) in enumerate(matrix):
        c = random.randint(17, 231)
        sys.stdout.write(cursor.position(y,x) + wrap(random.choice(arrows), fgcolor.xterm(c)))
        sys.stdout.flush()
        sys.stdout.write(cursor.position(height,1) + wrap("%d/%d" % (current+1, count), attr.faint))
        time.sleep(0.01)

if __name__ == '__main__':
    import sys
    import time
    import struct
    import termios
    import fcntl
    import random
    if sys.version_info[0] < 3:
        input = raw_input
    demo_colors()
    input(wrap("\nHit enter to continue", attr.bright) + cursor.hide)
    demo_cursor()
    input(cursor.up + cursor.column(1) + wrap("\nHit enter to continue", attr.bright) + cursor.hide)
    print(cursor.show + erase_display('all'))

del demo_colors
del demo_cursor
