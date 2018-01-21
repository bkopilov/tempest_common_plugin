
import json

from collections import defaultdict


class JsonManager(object):
    """
    JsonManager is a way to store all openstack objects into file
    and reuse the data inside the file or compare.
    Evrey object client from tempest is stored as is in the json dictionay
    list .
    """

    def __init__(self, file_location, permission="w"):
        self.store_file_location = file_location
        self.dict_store = defaultdict(list)
        self._create_file_json(permission)

    def _create_file_json(self, permission):
        try:
            self.fp = open(self.store_file_location, permission)
        except Exception as e:
            raise RuntimeError("Unable to open file %s %s"
                               % (self.store_file_location, str(e)))

    def dump_to_file(self):
        try:
            json.dump(self.dict_store, self.fp)
        except Exception as e:
            raise RuntimeError("Failed to write %s %s"
                               % (self.store_file_location, str(e)))

    def close_file(self):
        try:
            self.fp.close()
        except Exception as e:
            raise RuntimeError("Failed to close json file %s %s" %
                               (self.store_file_location, str(e)))

    def load_from_file(self):
        try:
            self.dict_store = json.load(self.fp)
            return self.dict_store
        except Exception as e:
            raise RuntimeError("Failed to load data from json file %s %s" %
                               (self.store_file_location, str(e)))

    def store_object(self, key, object_values):
        self.dict_store[key].append(object_values)

    def _store_objects_by_client(self, client_list,
                                 client_show_function, show_key=None):
        for value in client_list:
            if show_key:
                client_show = client_show_function(value['id'])[show_key]
            else:
                client_show = client_show_function(value['id'])
            # admin has different tenant ids.
            if client_show.get('links'):
                del client_show['links']
            self.store_object(client_show_function.im_class.__name__,
                              client_show)

    def capture_setup_by_clients(self, os_admin, close_fp=True):
        """We capture openstack clients
        Run list all objects per client and show detailed info per id.
        The output is added to the dictionary and stored in a file

        :param os_admin: client manager access to all clients
        :param close_fp:  close connection to file
        :return:
        """
        # Need to create a generic code. - TBD
        params = {"all_tenants": True}
        # capture all volumes
        volume_client = os_admin.volumes_client_latest
        self._store_objects_by_client(
            volume_client.list_volumes(params=params)['volumes'],
            volume_client.show_volume, 'volume')
        # capture all volume snapshots
        snapshot_client = os_admin.snapshots_client_latest
        self._store_objects_by_client(
            snapshot_client.list_snapshots(**params)['snapshots'],
            snapshot_client.show_snapshot, 'snapshot')
        # capture all instances
        server_client = os_admin.servers_client
        self._store_objects_by_client(
            server_client.list_servers(detail=True,
                                       **params)['servers'],
            server_client.show_server, 'server')
        # capture all networks
        network_clients = os_admin.networks_client
        self._store_objects_by_client(
            network_clients.list_networks(detail=True)['networks'],
            network_clients.show_network, 'network')
        # capture port lists
        port_client = os_admin.ports_client
        self._store_objects_by_client(
            port_client.list_ports()['ports'],
            port_client.show_port, 'port')

        # capture all glance images
        image_client = os_admin.image_client_v2
        self._store_objects_by_client(
            image_client.list_images()['images'],
            image_client.show_image)
        self.dump_to_file()

        if close_fp:
            self.close_file()
