#
# core.py
#
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
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
# 	Boston, MA    02110-1301, USA.
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

import deluge.component as component
from deluge.log import LOG as log


#special purpose filters:
def filter_keyword(torrent_ids, values):
    keywords = [v.lower() for v in values] #cleanup.
    all_torrents = component.get("TorrentManager").torrents
    #filter:
    for keyword in keywords:
        for torrent_id in torrent_ids:
            if keyword in all_torrents[torrent_id].filename.lower():
                yield torrent_id

def filter_state_active(self, torrent_ids, value):
    pass

class FilterManager(component.Component):
    """FilterManager

    """
    def __init__(self, core):
        component.Component.__init__(self, "FilterManager")
        log.debug("FilterManager init..")
        self.core = core
        self.torrents = core.torrents
        self.registered_filters = {}
        self.register_filter("keyword", filter_keyword)
        self.tree_fields = {}

        self.register_tree_field("state", self._init_state_tree)
        self.register_tree_field("tracker_host")

    def filter_torrent_ids(self, filter_dict):
        """
        returns a list of torrent_id's matching filter_dict.
        core filter method
        """
        if not filter_dict:
            return self.torrents.get_torrent_list()

        if "id"in filter_dict: #optimized filter for id:
            torrent_ids = filter_dict["id"]
            del filter_dict["id"]
        else:
            torrent_ids = self.torrents.get_torrent_list()

        if not filter_dict: #return if there's  nothing more to filter
            return torrent_ids

        #Registered filters:
        for field, values in filter_dict.items():
            if field in self.registered_filters:
                # a set filters out the doubles.
                torrent_ids = list(set(self.registered_filters[field](torrent_ids, values)))
                del filter_dict[field]

        if not filter_dict: #return if there's  nothing more to filter
            return torrent_ids

        #leftover filter arguments:
        #default filter on status fields.
        if filter_dict:
            status_func = self.core.export_get_torrent_status #premature optimalisation..
            for torrent_id in list(torrent_ids):
                status = status_func(torrent_id, filter_dict.keys()) #status={key:value}
                for field, values in filter_dict.iteritems():
                    if (not status[field] in values) and torrent_id in torrent_ids:
                        torrent_ids.remove(torrent_id)

        return torrent_ids

    def get_filter_tree(self):
        """
        returns {field: [(value,count)] }
        for use in sidebar.
        """
        torrent_ids = self.torrents.get_torrent_list()
        status_func = self.core.export_get_torrent_status #premature optimalisation..
        tree_keys = self.tree_fields.keys()
        items = dict( (field, init_func()) for field, init_func in self.tree_fields.iteritems())

        #count status fields.
        for torrent_id in list(torrent_ids):
            status = status_func(torrent_id, tree_keys) #status={key:value}
            for field in tree_keys:
                value = status[field]
                items[field][value] = items[field].get(value, 0) + 1

        for field in tree_keys:
            items[field] = sorted(items[field].iteritems())

        return items

    def _init_state_tree(self):
        return {"All":len(self.torrents.get_torrent_list()),
            "Downloading":0,
            "Seeding":0,
            "Paused":0,
            "Checking":0,
            "Queued":0,
            "Error":0}

    def register_filter(self, id, filter_func, filter_value = None):
        self.registered_filters[id] = filter_func

    def deregister_filter(self, id):
        del self.registered_filters[id]

    def register_tree_field(self, field, init_func = lambda : {}):
        self.tree_fields[field] = init_func

    def deregister_tree_field(self, field):
        del self.tree_fields[field]