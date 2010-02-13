#!/usr/bin/perl
# nagios_uptime_report.pl (aka nagios2mgmt.pl)
#
# Mail uptime graphs for a host to a set of addresses. Useful to
# keep curious managers at a distance.
#
# 1) Run this script from cron on 01:00 on the first of every month.
# 2) Make management receive this mail
# 3) ???
# 4) Profit

use strict;
use warnings;
use POSIX qw(mktime);
use MIME::Lite;
use LWP::Simple;

# "config"
my $from = '"Nagios uptime graphs" <noreply@example.com>';
my $subject = 'Nagios uptime graphs for %d/%d',
my @recipients = ('me@example.com',
                  'you@example.com');

my $nagios_host = 'http://user:pass@nagios.example.com';
my @hosts = ('www.example.com','test.example.com','mail.example.com');

# Here's where to get the graphs
my $baseurl = "https://$nagios_host/nagios/cgi-bin/trends.cgi?createimage" .
              '&assumeinitialstates=yes&assumestatesduringnotrunning=yes&initialassumedhoststate=0&' .
              'initialassumedservicestate=0&assumestateretention=yes&includesoftstates=no' .
              '&host=%s&backtrack=4&zoom=4&t1=%d&t2=%d';

# Which month to graph
# - Previous month if no month given
# - Allow overrides in argv, ./$0 year month
my $year = $ARGV[0];
my $month = $ARGV[1];
my ($cursec, $curmin, $curhour, $curmday, $curmon, $curyear, $curwday, $curyday, $curisdst) = gmtime(time);
$year = $curyear + 1900 if not defined $year;
$month = $curmon if not defined $month;
my $t1 = mktime(0, 0, 0, 1, $month-1, $year - 1900, 0, 0, 0);
my $t2 = mktime(0, 0, 0, 1, $month, $year - 1900, 0, 0, 0);

# Construct mail
my $msg = MIME::Lite->new(
    From => $from,
    To => join(',', @recipients),
    Subject => sprintf($subject, $year, $month),
    Type => 'multipart/related',
);
$msg->attach(
    Type => 'text/html',
    Data => '<body>' . join('<br />', map(sprintf('<img src="cid:%s.png" />', $_), @hosts)) . '</body>'
);

# Fetch images and attach
foreach my $host (@hosts) {
    my $url = sprintf $baseurl, $host, $t1, $t2;
    my $img = get($url);
    $msg->attach(
        Type => 'image/png',
        Data => $img,
        Id  => "$host.png",
    );
}

# Send!
$msg->send();
