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
from tempest.lib import decorators

from tempest_common_plugin.common.utils.linux.json_actions\
    import JsonManager
from tempest_common_plugin.tests.scenario import manager

CONF = config.CONF


class PrepareCloudActions(manager.ScenarioTest):
    """
    Prepare cloud actions test create a cloud setup without cleanup
    We create image, volumes , snapshots and instances per user request
    from tempest.conf file .
    Once all resources are created, we run show on "needed" clients and
    store all data into json file , we store the data as is in a list of
    dictionaries .
    In order to re-use these test all created with a single tenants configured
    in account.yaml and we set use_dynamic_credentials to false

    This testcase run before we call to cloud tests as tempest or upgrade ...

    Example:
        Prepare cloud
        --- run tests - tempest, upgrade, update , restart ---
        Verify cloud - load old json and compare to current latest.
        Post verify - Reuse existing object loaded from prepare phase.
    """
    credentials = ['primary', 'admin']

    @classmethod
    def resource_setup(cls):
        super(PrepareCloudActions, cls).resource_setup()
        # create a json file to write all objects
        cls.json_manager = JsonManager(
            file_location=CONF.prepare_cloud_setup.store_json_before,
            permission="w")

    @classmethod
    def resource_cleanup(cls):
        # by default tempest cleanup all resources
        # We disable tempest cleanups.
        cls.json_manager.capture_setup_by_clients(cls.os_admin)
        cls._disable_cls_cleanup()
        super(PrepareCloudActions, cls).resource_cleanup()

    @staticmethod
    def _get_bdm(source_id, source_type, delete_on_termination=False):
        bd_map_v2 = [{
            'uuid': source_id,
            'source_type': source_type,
            'destination_type': 'volume',
            'boot_index': 0,
            'delete_on_termination': delete_on_termination}]
        return {'block_device_mapping_v2': bd_map_v2}

    def _disable_self_cleanup(self):
        self._cleanups = []
        self._teardowns = []
        self._creds = {}

    @classmethod
    def _disable_cls_cleanup(cls):
        cls._cleanups = []
        cls._teardowns = []
        cls._creds = {}

    @decorators.idempotent_id('44a0696f-fb26-4cfc-b7d3-fce1ea03d044')
    def test_prepare_attached_volumes_snapshots(self):
        """Create a cloud storage setup volumes, snapshots glance instances.
        Nova boot from glance, volume and snapshot
        Its recommended to create the resources with public permissions
        for reusing in post verify state by other tenants.
        """
        for i in range(0, CONF.prepare_cloud_setup.volumes_create):
            # Create a volume and instance and instance snapshot
            volume_info = self.create_volume(imageRef=CONF.compute.image_ref)
            kwargs_volume = self._get_bdm(source_id=volume_info['id'],
                                          source_type="volume")
            server_info_volumes = self.create_server(image_id='',
                                                     **kwargs_volume)
            self.create_server_snapshot(server=server_info_volumes)
            # Create a snapshot from volume and instance from snapshot and
            # image snapshot
            snapshot_info = self.create_volume_snapshot(
                volume_id=volume_info['id'], force=True)
            kwargs_snapshot = self._get_bdm(source_id=snapshot_info['id'],
                                            source_type="snapshot",
                                            delete_on_termination=True)
            server_info_snapshot = self.create_server(image_id='',
                                                      **kwargs_snapshot)
            self.create_server_snapshot(server=server_info_snapshot)

        self._disable_self_cleanup()
