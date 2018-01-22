# Copyright 2018 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from tempest import config
from tempest.common import waiters
from tempest.lib import decorators

from tempest_common_plugin.common.capture_cloud.json_actions \
    import JsonManager
from tempest_common_plugin.tests.scenario import manager

CONF = config.CONF


class PostCloudActions(manager.ScenarioTest):
    """PostCloudAction will reuse old json file from prepareCloud phase
    In the json files we have all params about the object.
    The stored info is taked from client.show_xxx(object_id)
    Example of how it stored
    {"VolumesClient":[...],[...],
     "SnapshotsClient: [..][..]"}
    """
    credentials = ['primary', 'admin']

    @classmethod
    def _load_from_json(cls, file_location, permission):
        json_manager = JsonManager(file_location=file_location,
                                   permission=permission)
        data_from_json = json_manager.load_from_file()
        json_manager.close_file()
        return data_from_json

    @classmethod
    def resource_setup(cls):
        super(PostCloudActions, cls).resource_setup()
        cls.restored_cloud_before = cls._load_from_json(
            CONF.prepare_cloud_setup.store_json_before, "r")

    @classmethod
    def resource_cleanup(cls):
        super(PostCloudActions, cls).resource_cleanup()

    def _delete_servers(self, server_id):
        self.os_admin.servers_client.delete_server(server_id)
        waiters.wait_for_server_termination(self.os_admin.servers_client,
                                            server_id)

    def _delete_volumes(self, volume_id):
        self.os_admin.volumes_client_latest.delete_volume(volume_id, cascade=True)
        self.os_admin.volumes_client_latest.wait_for_resource_deletion(volume_id)

    def _delete_images(self, image_id):
        self.os_admin.image_client.delete_image(image_id)
        self.os_admin.image_client.wait_for_resource_deletion(image_id)

    @decorators.idempotent_id('94ee80ee-fd44-4b79-9ccc-cf17324157dc')
    def test_post_cloud_actions(self):
        # clean all resources
        images_id = [image['id']
                     for image in self.restored_cloud_before['ImagesClient']
                     if image['id'] not in
                     [CONF.compute.image_ref, CONF.compute.image_ref_alt]
                     ]
        cinder_ids = [cinder['id'] for cinder in
                      self.restored_cloud_before['VolumesClient']]
        servers_ids = [server['id'] for server in
                       self.restored_cloud_before['ServersClient']]

        map(self._delete_servers, servers_ids)
        map(self._delete_volumes, cinder_ids)
        map(self._delete_images, images_id)
