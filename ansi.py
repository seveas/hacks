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

fgcolor = Attr(black=30, red=31, green=32, yellow=33, blue=34, magenta=35, cyan=36, white=37, none=None)
bgcolor = Attr(black=40, red=41, green=42, yellow=43, blue=44, magenta=45, cyan=46, white=47, none=None)
attr    = Attr(normal=0, bright=1, faint=2, underline=4, negative=7, conceal=8, crossed=9, none=None)

esc = '\033'
mode = lambda *args: "%s[%sm" % (esc, ';'.join([str(x) for x in args if x is not None]))
reset = mode(attr.normal)
wrap = lambda text, *args: "%s%s%s" % (mode(*args), text, reset)

def demo():
    import sys
    for dattr in sorted(attr.attr):
        print "Demonstrating " + dattr
        for dfgcolor in fgcolor.attr:
            for dbgcolor in bgcolor.attr:
                sys.stdout.write(wrap(
                    " %7s %7s " % (dfgcolor, dbgcolor), 
                    getattr(fgcolor, dfgcolor),
                    getattr(bgcolor, dbgcolor),
                    getattr(attr, dattr)
                ))
            print ""
        print ""

if __name__ == '__main__':
    demo()
del demo
