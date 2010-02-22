# Sends highlights as a /query to yourself so they are all available in one tab
# (c)2010 Dennis Kaarsemaker <dennis@kaarsemaker.net>
# Licence: MIT

import fnmatch
import string
import xchat

__module_name__ = "hilight"
__module_version__ = "0.1"
__module_description__ = "Log highlighting messages to a /query to self"

rfc2812_tolower = string.maketrans('[]\\~','{}|^')
irc_lower = lambda txt: txt.lower().translate(rfc2812_tolower)

def on_msg(word, word_eol, userdata):
    sender=word[0][1:]
    recipient=word[2]
    message=word_eol[3][1:]
    if not is_highlight(sender, recipient, message):
        return xchat.EAT_NONE
    ctx = xchat.find_context(server=xchat.get_info('server'),channel=xchat.get_info('nick'))
    if not ctx:
        # Open a query if it isn't there yet
        xchat.command('query -nofocus %s' % xchat.get_info('nick'))
        ctx = xchat.find_context(server=xchat.get_info('server'),channel=xchat.get_info('nick'))
    if message[0] == message[-1] and message[0] == '\x01':
        # CTCP. Only honor CTCP action aka /me
        print message[1:7]
        if message[1:7].lower() != 'action':
            return xchat.EAT_NONE
        ctx.emit_print('Channel Action Hilight', '%s/%s' % (sender[:sender.find('!')], recipient), message[8:-1], '')
    else: 
        ctx.emit_print('Channel Msg Hilight', '%s/%s' % (sender[:sender.find('!')], recipient), message, '')
    return xchat.EAT_NONE
xchat.hook_server("PRIVMSG", on_msg)

def is_highlight(sender, recipient, message):
    """Are we being highlighted?"""
    message = irc_lower(message)
    sender = irc_lower(sender)
    # Only highlight channels
    if not recipient[0] in '#&@':
        return False
    # Nicks to never highlight
    nnh = irc_lower(xchat.get_prefs('irc_no_hilight') or '')
    if match_word(sender[:sender.find('!')], nnh.split(',')):
        return False
    # Nicks to always highlight
    nth = irc_lower(xchat.get_prefs('irc_nick_hilight') or '')
    if match_word(sender[:sender.find('!')], nth.split(',')):
        return True
    # Words to highlight on, masks allowed
    wth = [irc_lower(xchat.get_prefs('irc_nick%d' % x) or '') for x in (1,2,3)] + [irc_lower(xchat.get_info('nick'))]
    wth += irc_lower(xchat.get_prefs('irc_extra_hilight') or '').split(', ')
    for w in wth:
        if w in message:
            return True
    return False

def match_word(needle, haystack):
    # Evil. Use fnmatch. 
    haystack = [x.strip() for x in haystack if x.strip()]
    return bool(fnmatch.filter(haystack, needle))
