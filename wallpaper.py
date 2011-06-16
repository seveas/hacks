#!/usr/bin/python
#
# Grab a random desktop background from interfacelift.com with the correct
# resolution and set it as background. Requirements: xrandr, gnome
#
# (c) 2010 Dennis Kaarsemaker

import cStringIO as stringio
import glob
import os
from PIL import Image
import random
import re
import stat
import sys
import subprocess
import urllib2

DOWNLOAD_PATH = '/home/dennis/Pictures'
INDEX = "http://interfacelift.com/wallpaper_beta/downloads/date/any/"
DOWNLOAD_BASE = "http://interfacelift.com/wallpaper_beta/grab/"
GCONF_KEY = "/desktop/gnome/background/picture_filename"

def get_resolution():
    xrandr_output = subprocess.Popen(["/usr/bin/xrandr"],stdout=subprocess.PIPE).communicate()[0]
    resolution = re.search(r"current\s+(\d+ x \d+)", xrandr_output).group(1)
    return resolution.replace(' ','')

def set_background(path):
    # Lazy!
    subprocess.call(["gconftool-2", "--set", GCONF_KEY, "--type", "string", path])

def set_gdm_background(path):
#    from gdm2.gdm2gconf import GDM2Theme as gt
#    gt = gt()
#    gt.DEBUG = False
#    gt.SetWallpaper(path, False)
    with open('/usr/share/images/xsplash/bg.jpg','w') as wfd:
        with open(path, 'r') as rfd:
            wfd.write(rfd.read())

def import_env(find_exe):
    for d in os.listdir('/proc'):
        if not d.isdigit():
            continue
        d = os.path.join('/proc', d)
        try:
            exe = os.readlink(os.path.join(d, 'exe'))
        except OSError:
            continue
        if exe == find_exe:
            uid = os.stat(d)[stat.ST_UID]
            env = open(os.path.join(d, 'environ')).read()
            env = dict([x.split('=', 1) for x in env.split('\x00') if x])
            os.environ.update(env)
            return uid
    else:
        print "Process %s not running" % find_exe
        sys.exit(1)

class InterfaceLift(object):
    def update(self, resolution):
        for i in range(5):
            try:
                page = self.random_page()
                id_name = self.random_image(page)
                return self.download_image(id_name, resolution)
            except IOError: # Bad image
                continue
            except urllib2.URLError: # Not online?
                break
        pictures = glob.glob(os.path.join(DOWNLOAD_PATH, '*_%s.*' % resolution))
        if not pictures:
            return None
        return random.choice(pictures)

    def random_page(self):
        html = urllib2.urlopen(INDEX).read()
        pages = re.search("page \d+ of (\d+)", html).group(1)
        rand = random.randint(1, int(pages))
        html = urllib2.urlopen("%sindex%d.html" % (INDEX, rand)).read()
        return html
    
    def random_image(self, html):
        images = re.findall('<img[^>]*previews/(.*?)"', html)
        return random.choice(images)
    
    def download_image(self, name, resolution):
        name, ext = name.rsplit('.', 1)
        name = '%s_%s.%s' % (name, resolution, ext)
        dpath = os.path.join(DOWNLOAD_PATH, name)
        if not os.path.exists(dpath):
            img = urllib2.urlopen(DOWNLOAD_BASE + name).read()
            Image.open(stringio.StringIO(img))
            with open(dpath, 'w') as fd:
                fd.write(img)
        return dpath

def main():
    uid = import_env('/usr/bin/nautilus')
    resolution = get_resolution()
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        klass = InterfaceLift # In the future there could be more classes
        path = klass().update(resolution)
    if path:
        if os.geteuid() == 0:
            set_gdm_background(path)
            os.setuid(uid)
        set_background(path)

if __name__ == '__main__':
    main()
