Collection of hacks
===================

This is a collection of small hacks I wrote over the years.

check_trace
-----------
Nagios plugin to resolve a check whether a hostname is fully resolvable, from
the root nameservers down to the authoritative nameserver for the domain. On
more than one occasion, SIDN broke the .nl zone, making this check useful.

hilight.py
----------
xchat script that copies all hilighting messages to a /query to yourself

launchpadduser
--------------
create local accounts based on launchpad accounts

nagios_uptime_report.pl 
-----------------------
A management pacifier, mail them uptime graphs monthly to keep them happy (or
sad, if you didn't do your job properly).

pcat
----
A cat that works on fifos (created with mkfifo).

reset_password
--------------
Boot from a live cd and run this to reset all passwords it finds.

shell.py
--------
A pythonic version of perls 'use Shell;'. Syntaxtic sugar around subprocess
that makes creating processes and pipelines even easier.

singleton.py
------------
Pure-python subclassablie singleton class that uses __new__ instead of the
usual __init__+impl tkrick, so they are real singletons.
