#!/usr/bin/python
"""
Script to go through the javascript files and dynamically generate gettext.js
"""
import os
import re

output_file = "gettext.js"
string_re = re.compile('_\\(\'(.*?)\'\\)')
strings = {}


gettext_tpl = """## -*- coding: utf-8 -*-
/*
 * Script: gettext.js
 *  A script file that is run through the template renderer in order for
 *  translated strings to be used.
 *
 * Copyright:
 *  (c) 2009 Damien Churchill <damoxc@gmail.com>
 */

GetText = {
    maps: {},
    add: function(string, translation) {
        this.maps[string] = translation;
    },
    get: function(string) {
        if (this.maps[string]) {
            return this.maps[string];
        } else {
            return string;
        }
    }
}

function _(string) {
    return GetText.get(string);
}

"""

for root, dnames, files in os.walk('js/deluge-all'):
    for filename in files:
        if filename.startswith('.'):
            continue
        if not filename.endswith('.js'):
            continue

        for lineno, line in enumerate(open(os.path.join(root, filename))):
            for match in string_re.finditer(line):
                string = match.group(1)
                locations = strings.get(string, [])
                locations.append((os.path.basename(filename), lineno + 1))
                strings[string] = locations


keys = strings.keys()
keys.sort()

fp = open(output_file, 'w')
fp.write(gettext_tpl)
for key in keys:
    fp.write('// %s\n' % ', '.join(map(lambda x: '%s:%s' % x, strings[key])))
    fp.write("GetText.add('%(key)s', '${escape(_(\"%(key)s\"))}')\n\n" % locals())
fp.close()

