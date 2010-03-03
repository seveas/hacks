import dns.resolver
import dns.reversename
import re
import socket
import struct
import xchat

__module_name__ = "gateway_identify"
__module_description__ = "Print the IP of users joining from gateways"
__module_version__ = "1.0"

hex_ip_regex = re.compile(r'^~?[0-9a-f]{8}$')
def make_ip(s):
    return socket.inet_ntoa(struct.pack('!I',eval('0x'+s)))

def identify_gateway(word, word_eol, userdata):
    id = word[0][1:]
    nick, ident, host = re.split('[@!]', id)
    if not (hex_ip_regex.match(ident) and host.startswith('gateway/')):
        return
    channel = word[-1][1:]
    ip = make_ip(ident[-8:])
    print ip
    try:
        host = dns.resolver.query(dns.reversename.from_address(ip), 'PTR').response.answer[0][0].to_text()[:-1]
    except dns.resolver.NXDOMAIN:
        host = 'unknown hostname'
    xchat.find_context(channel=channel).emit_print('Server Notice', "%s is coming from %s (%s)" % (nick, ip, host))
xchat.hook_server('JOIN', identify_gateway, priority=xchat.PRI_LOWEST)
