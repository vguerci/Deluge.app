#!/usr/bin/env python
import re, sys

def color(string, fg=None, attrs=[], bg=None, keep_open=False):
    if isinstance(attrs, basestring):
        attrs = [attrs]
    attrs = map(str.lower, attrs)
    ansi_reset = "\x1b[0m"
    if len(attrs) == 1 and 'reset' in attrs:
        return ansi_reset
    colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    attributes = ['reset', 'bright', 'dim', None, 'underscore', 'blink', 'reverse', 'hidden']
    _fg = 30 + colors.index(fg.lower()) if fg and fg.lower() in colors else None
    _bg = 40 + colors.index(bg.lower()) if bg and bg.lower() in colors else None
    _attrs = [ str(attributes.index(a)) for a in attrs if a in attributes]
    color_vals = map(str, filter(lambda x: x is not None, [_fg, _bg]))
    color_vals.extend(_attrs)
    reset_cmd = ansi_reset if not keep_open else ''
    return "\x1b["+";".join(color_vals)+"m"+string+reset_cmd

def make_style(*args, **kwargs):
    return lambda text: color(text, *args, **kwargs)

default_style = {
    'black' : make_style(fg='black'),
    'red' : make_style(fg='red'),
    'green' : make_style(fg='green'),
    'yellow' : make_style(fg='yellow'),
    'blue' : make_style(fg='blue'),
    'magenta' : make_style(fg='magenta'),
    'cyan' : make_style(fg='cyan'),
    'white' : make_style(fg='white'),
    
    'bold_black' : make_style(fg='black', attrs='bright'),
    'bold_red' : make_style(fg='red', attrs='bright'),
    'bold_green' : make_style(fg='green', attrs='bright'),
    'bold_yellow' : make_style(fg='yellow', attrs='bright'),
    'bold_blue' : make_style(fg='blue', attrs='bright'),
    'bold_magenta' : make_style(fg='magenta', attrs='bright'),
    'bold_cyan' : make_style(fg='cyan', attrs='bright'),
    'bold_white' : make_style(fg='white', attrs='bright'),
}

class Template(str):
    regex = re.compile(r'{{\s*(?P<style>.*?)\((?P<arg>.*?)\)\s*}}')
    style = default_style
    def __new__(self, text):
        return str.__new__(self, Template.regex.sub(lambda mo: Template.style[mo.group('style')](mo.group('arg')), text))

    def __call__(self, *args, **kwargs):
        if kwargs:
            return str(self) % kwargs
        else:
            return str(self) % args

class struct(object):
    pass

templates = struct()
templates.prompt = Template('{{bold_white(%s)}}')
templates.ERROR = Template('{{bold_red( * %s)}}')
templates.SUCCESS = Template('{{bold_green( * %s)}}')
templates.help = Template(' * {{bold_blue(%-*s)}} %s')
templates.info_general = Template('{{bold_blue(*** %s:)}} %s')
templates.info_transfers = Template('{{bold_green(*** %s:)}} %s')
templates.info_network = Template('{{bold_white(*** %s:)}} %s')
templates.info_files_header = Template('{{bold_cyan(*** %s:)}}')
templates.info_peers_header = Template('{{bold_magenta(*** %s:)}}')
templates.info_peers = Template('\t * {{bold_blue(%-22s)}} {{bold_green(%-25s)}} {{bold_cyan(Up: %-12s)}} {{bold_magenta(Down: %-12s)}}')
templates.config_display = Template(' * {{bold_blue(%s)}}: %s')