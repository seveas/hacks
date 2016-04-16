Collection of hacks
===================

This is a collection of small hacks I wrote over the years.

ansi.py
-------
ANSI terminal colors demo. Glorified readme, reusable as lib.

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

fake_time.c
-----------
Make your system think differently about time.

gateway_identify.py
-------------------
xchat script that prints the IP address/hostname of users connecting from a
known gateway on freenode.

git-ssh
-------
Easy ssh access to remote git hosts and repos.

gnome-keyring-dump
------------------
Dump the contents of the gnome keyring

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

NetworkManager/dispatcher.d/autologin
-------------------------------------
Automatically log in to wireless networks that have a captive portal. This
script doesn't actually login, but dispatches to actual login scripts.

NetworkManager/dispatcher.d/synergy
-----------------------------------
Autostart synergy when connected to the right network

NetworkManager/autologin.d/wifi_in_de_trein
-------------------------------------------
Automatically log in to the wifi in dutch trains.

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

singleton.py
------------
Pure-python subclassable singleton class that uses __new__ instead of the
usual __init__+impl trick (borg pattern), so they are real singletons.

stealenv.py
-----------
Steal (well, output) a process in a variety of formats, usable by shells and
other languages.

subsetsum.py
------------
Find a subset of a set of integers with a given sum. Useful for "for €50 in
receipts, you get a free something".

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
