# Copyright 2017 Red Hat, Inc.
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

from tempest_common_plugin.tests.api.volume import base

CONF = config.CONF


class VolumesSnapshotTestJSON(base.BaseVolumeTest):

    @classmethod
    def skip_checks(cls):
        super(VolumesSnapshotTestJSON, cls).skip_checks()
        if not CONF.volume_feature_enabled.snapshot:
            raise cls.skipException("Cinder volume snapshots are disabled")

    @decorators.idempotent_id('f70ab375-921f-43f1-89aa-b58ec8f79724')
    def test_snapshot_create_after_volume_extend(self):
        # Create a volume
        volume = self.create_volume()

        # Extend the volume
        extend_size = volume['size'] + 1
        self.volumes_client.extend_volume(volume_id=volume['id'],
                                          new_size=extend_size)
        waiters.wait_for_volume_resource_status(self.volumes_client,
                                                volume['id'], 'available')

        # Verify snapshot is created successfully with the correct size
        snapshot = self.create_snapshot(volume_id=volume['id'])
        self.assertEqual(extend_size, snapshot['size'])

    @decorators.idempotent_id('0c6a3d56-85dc-454d-ad93-f4b713a66fc2')
    def test_snapshot_create_volume_description_non_ascii_code(self):
        # Create a volume with non-ascii description
        description = u'\u05e7\u05d9\u05d9\u05e4\u05e9'
        volume = self.create_volume(description=description)
        vol_info = self.volumes_client.show_volume(volume['id'])['volume']
        self.assertEqual(description, vol_info['description'])
        self.create_snapshot(volume['id'])
