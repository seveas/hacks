#!/usr/bin/python
#
# Grab a random desktop background and set it as background. Requirements: xrandr, gnome, PIL
#
# (c) 2010-2013 Dennis Kaarsemaker

import cStringIO as stringio
import glob
import os
from   PIL import Image
import random
import re
import stat
import stealenv
import sys
import requests
from   whelk import shell

requests.utils.default_user_agent = lambda: 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:20.0) Gecko/20100101 Firefox/20.0'
download_path = '/home/dennis/Pictures/wallpapers'

class DownloadError(Exception):
    pass

class IfLift(object):
    index = "aHR0cDovL2ludGVyZmFjZWxpZnQuY29tL3dhbGxwYXBlci9kb3dubG9hZHMvZGF0ZS9hbnkv==".decode('base64')
    download_base = "aHR0cHM6Ly9pbnRlcmZhY2VsaWZ0LmNvbS93YWxscGFwZXIvN3l6NG1hMS8=".decode('base64')

    def random_image(self, resolution):
        html = requests.get(self.index).text
        pages = max([int(x) for x in re.findall("index(\d+)\.html", html)])
        rand = random.randint(1, int(pages))
        html = requests.get("%sindex%d.html" % (self.index, rand)).text
        images = re.findall('<img[^>]*previews/(.*?)"', html)
        name,ext = random.choice(images).rsplit('.', 1)
        name = name.rsplit('_', 1)[0]
        name = '%s_%s.%s' % (name, resolution, ext)
        dpath = os.path.join(download_path, name)
        if not os.path.exists(dpath):
            img = requests.get(self.download_base + name).content
            Image.open(stringio.StringIO(img))
            with open(dpath, 'w') as fd:
                fd.write(img)
        return dpath

def main():
    uid = stealenv.from_name('/usr/bin/nautilus')
    resolution = re.search(r"current\s+(\d+ x \d+)", shell.xrandr().stdout).group(1).replace(' ', '')
    path = None

    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        klass = IfLift # In the future there could be more classes
        try:
            path = klass().random_image(resolution)
        except DownloadError:
            pictures = glob.glob(os.path.join(download_path, '*_%s.*' % resolution))
            if pictures:
                path = random.choice(pictures)
    if path:
        shell.gsettings("set", "org.gnome.desktop.background", "picture-uri", "file://" + os.path.abspath(path))
    else:
        print "No image found"

if __name__ == '__main__':
    main()
