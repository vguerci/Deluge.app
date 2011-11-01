#
# osx.py
#
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#
#
from deluge.ui.gtkui.gtkui import reactor

from deluge.log import LOG as log
from deluge.ui.client import client

import gtk_osxapplication

class OSX(object):
    def __init__(self, gtkui):
        log.debug('integrating')
        self.gtkui = gtkui
        self.osxapp = gtk_osxapplication.OSXApplication()
        self.connect()
        self.osxapp.ready()

    def connect(self):
        self.osxapp.connect("NSApplicationOpenFile", self.open_file)
        self.osxapp.connect("NSApplicationBlockTermination", self.quit)

    # from http://sourceforge.net/mailarchive/forum.php?thread_name=AANLkTikUhZpPrg6VdXu64QBw8V1iGTXd5oZ6NCT%2BYrkv%40mail.gmail.com&forum_name=gtk-osx-users
    def open_file(self, osxapp, filename):
        # Will be raised at app launch (python opening main script)
        if filename.endswith('Deluge-bin'):
            return True

        def on_show(result):
            self.gtkui.addtorrentdialog.add_from_files([filename])
        def show():
            d = self.gtkui.addtorrentdialog.show(self.gtkui.config["focus_add_dialog"])
            d.addCallback(on_show)

        if not client.connected():
            log.debug('queuing file %s', filename)
            self.gtkui.queuedtorrents.add_to_queue([filename])
        else:
            log.debug('opening file %s', filename)
            show() # doesn't look like required anymore: gobject.idle_add(show)
        return True

    def quit(self, *args):
        log.debug('quit')
        self.gtkui.shutdown()
        reactor.stop()
        return False
