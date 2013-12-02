Collection of hacks
===================

This is a collection of small hacks I wrote over the years.

ansi.py
-------
ANSI terminal colors demo. Glorified readme, reusable as lib.

buienradar
----------
Tiny PyGTK app that downloads and displays dutch or west-european radarimages
that show where it rains. Loops over 1-24 hours worth of images and has
keyboard control.

check_trace
-----------
Nagios plugin to resolve a check whether a hostname is fully resolvable, from
the root nameservers down to the authoritative nameserver for the domain. On
more than one occasion, SIDN broke the .nl zone, making this check useful.

clientbucket_to_git
--------------------
Converts a puppet clientbucket to a git repository for easy inspection of
server changes over time.

cisco-crypt.py
--------------
Python module and standalone script for encrypting/decrypting cisco-style
encrypted passwords in .pcf files for the vpn client.

deletepassphrases
-----------------
Make networkmanager forget passwords immediately after authenticating. This
really should be a feature in n-m itself but sadly isn't. (The feature does
exists in the most recent version of n-m)

fake_time.c
-----------
Make your system think differently about time.

gateway_identify.py
-------------------
xchat script that prints the IP address/hostname of users connecting from a
known gateway on freenode.

hilight.py
----------
xchat script that copies all hilighting messages to a separate channel-like
window.

launchpadduser
--------------
create local accounts based on launchpad accounts.

mutt-ldapsearch
---------------
Search e-mail addresses in ldap from mutt

mutt-keyring
------------
Make mutt use gnome-keyring for passwords

nagios_uptime_report.pl 
-----------------------
A management pacifier, mail them uptime graphs monthly to keep them happy (or
sad, if you didn't do your job properly).

nma.pl
------
Send irssi notifications to your android phone when screen is detached.

p2000
-----
Script to monitor and alert on p2000 (dutch emergency services) messages.

pcat.c
------
A cat that works on fifos (created with mkfifo).

progressbar.py
--------------
Python library for creating smooth progressbars on the terminal using unicode
characters for sub-character precision.

rainbow
-------
Colorize output with a rainbow pattern. For those boring days.

reset_passwords
---------------
Boot from a live cd and run this to reset all passwords it finds.

run-single-cron
---------------
Runs a single job from a crontab exactly as cron would do it

shell.py
--------
A pythonic version of perls 'use Shell;'. Syntaxtic sugar around subprocess
that makes creating processes and pipelines even easier.

singleton.py
------------
Pure-python subclassable singleton class that uses __new__ instead of the
usual __init__+impl trick (borg pattern), so they are real singletons.

stealenv.py
-----------
Steal (well, output) a process in a variety of formats, usable by shells and
other languages.

suid_script_wrapper.c
---------------------
When sudo is not available, you can use this to let people run a script as
another user.

wag.c
-----
Poor-mans file watcher. Whenever a file changes, execute an application. Made
for systems where inotify does not exist.

wallpaper.py
------------
Random wallpaper grabber & changer. Supports only interfacelift.com for now.
