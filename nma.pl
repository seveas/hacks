# nma.pl - Send notifications to your android phone when screen is detached
# (c) 2013 Dennis Kaarsemaker <dennis@kaarsemaker.net>
# Bugs can be filed at github.com/seveas/hacks
#
# Prep work: 
# - Get an account on notifymyandroid.com
# - Buy a premium account (cheap, one time purchase) if you want to receive
#   more than 5 notifications per day
# - Install the app on your android device(s)
# - Generate an API key
#
# Usage:
# - /load nma.pl
# - /set nma_api_key your_key_goes_here
# - /save
#
# When that is all done, all private messages and all public messages that
# contain your nickname will be sent to your android device(s).

use strict;
use warnings;

use Irssi;
use LWP::UserAgent;
use POSIX qw(access X_OK);

use vars qw($VERSION %IRSSI $screen_socket);

$VERSION = "1.0";
%IRSSI = (
    authors     => "Dennis Kaarsemaker",
    contact     => "dennis\@kaarsemaker.net",
    name        => "nma",
    description => "Send a notification to android devices via notifymyandroid",
    license     => "GPLv3",
    url         => "https://github.com/seveas/nma.pl"
);

check_screen();
check_tmux();
Irssi::settings_add_str("nma", "nma_api_key", "");
Irssi::signal_add_last('message private', 'private');
Irssi::signal_add_last('message public', 'public');

# Code inspired by screen_away.pl
sub check_screen {
    return unless defined($ENV{STY});

    my $socket = `LC_ALL="C" screen -ls`;
    return if $socket =~ /^No Sockets found/s;

    $socket =~ s/^.+\d+ Sockets? in (.*?)\/?\.\n.+$/$1/s;
    $socket .= "/" . $ENV{STY};
    $screen_socket = $socket;
}
sub check_tmux {
    return unless defined($ENV{TMUX});
    $screen_socket = $ENV{TMUX};
    $screen_socket =~ s/(,\d+)+$//;
}

sub screen_detached { $screen_socket && !access($screen_socket, X_OK) }

sub private {
    my ($server, $msg, $nick, $address) = @_;
    return unless screen_detached;
    send_message($server->{tag}, "Private message from $nick", $msg);
}

sub public {
    my ($server, $msg, $nick, $address, $target) = @_;
    return unless screen_detached;
    return unless $msg =~ /\Q$server->{nick}\E/i;
    send_message($server->{tag}, "Message from $nick in $target", $msg);
}

sub send_message {
    my ($server, $title, $message) = @_;

    my $key = Irssi::settings_get_str("nma_api_key");
    return unless $key;

    my $ua = LWP::UserAgent->new();
    $ua->env_proxy();
    $ua->agent("irssi/$Irssi::VERSION");

    my $resp = $ua->post("https://nma.usk.bz/publicapi/notify", {
        apikey => $key,
        application => "IRC: $server",
        priority => 0,
        event => $title,
        description => $message});
}
