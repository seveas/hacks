# Yum plugin that warns when you're about to overwrite files that are managed
# by puppet.
#
# Usage:
# - Place this file in /usr/lib/yum-plugins
# - Put the following in /etc/yum/pluginconf.d/puppet.conf
#
# [main]
# enabled=1
# puppet_state_file=/var/lib/puppet/state/state.yaml
#
# And use yum like you normally would.

from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE
import yaml

def generic_string_constructor(loader, node):
    return loader.construct_scalar(node)
yaml.add_constructor(u'!ruby/sym', generic_string_constructor)

requires_api_version = '2.5'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)

def config_hook(conduit):
    global puppet_files
    puppet_state_file = conduit.confString('main', 'puppet_state_file', default='/var/lib/puppet/state/state.yaml')
    yaml_data = yaml.load(open(puppet_state_file, 'r').read())
    puppet_files = [x[5:-1] for x in yaml_data.keys() if x.startswith('File[')]

def pretrans_hook(conduit):
    ts = conduit.getTsInfo()
    packages = ts.updated + ts.installed + ts.depinstalled + ts.depupdated + ts.reinstalled + ts.downgraded
    prompt = []
    for p in packages:
        for file in p.po.filelist:
            if file in puppet_files:
                prompt.append("Installing %s overwrites puppet-managed file %s" % (str(p.po), file))
    if prompt:
        if not conduit.promptYN('\n'.join(prompt)):
            raise PluginYumExit('Aborting')
