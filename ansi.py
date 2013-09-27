# Stupid ansi color demo program 'cause I keep forgetting them
# And it's reusable as a library too. Whaddayaknow.

class Attr(object):
    def __init__(self, **attr):
        self.attr = attr
        self.rev_attr = dict([(v,k) for k,v in attr.items()]) 
        for k, v in attr.items():
            setattr(self, k, v)

    def name(self, val):
        return self.rev_attr[val]

class Color(Attr):
    def xterm(self, val):
        return '%d;5;%d' % (self._xterm, val)

fgcolor = Color(black=30, red=31, green=32, yellow=33, blue=34, magenta=35, cyan=36, white=37, _xterm=38, default=39, none=None)
bgcolor = Color(black=40, red=41, green=42, yellow=43, blue=44, magenta=45, cyan=46, white=47, _xterm=48, default=49, none=None)
attr    = Attr(normal=0, bright=1, faint=2, underline=4, negative=7, conceal=8, crossed=9, none=None)

esc = '\033'
mode = lambda *args: "%s[%sm" % (esc, ';'.join([str(x) for x in args if x is not None]))
reset = mode(attr.normal)
wrap = lambda text, *args: "%s%s%s" % (mode(*args), text, reset)

erase_line = esc + '[K'
erase_display = esc + '[2J'
save_cursor = esc + '[s'
restore_cursor = esc + '[u'

def demo():
    import sys
    for dattr in sorted(attr.attr):
        if dattr == 'none':
            continue
        print("Demonstrating " + dattr)
        for dfgcolor in fgcolor.attr:
            if dfgcolor in ('none', '_xterm', 'default'):
                continue
            for dbgcolor in bgcolor.attr:
                if dbgcolor in ('none', '_xterm', 'default'):
                    continue
                sys.stdout.write(wrap(
                    " %7s %7s " % (dfgcolor, dbgcolor), 
                    getattr(fgcolor, dfgcolor),
                    getattr(bgcolor, dbgcolor),
                    getattr(attr, dattr)
                ))
            print("")
        print("")

    print("Xterm color palette")
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
    print("")

if __name__ == '__main__':
    demo()
del demo
