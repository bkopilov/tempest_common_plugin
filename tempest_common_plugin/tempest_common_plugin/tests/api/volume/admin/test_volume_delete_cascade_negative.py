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

import testtools

from tempest import config
from tempest.lib import decorators
from tempest.lib import exceptions as lib_exc

from tempest_common_plugin.tests.api.volume import base

CONF = config.CONF


class VolumesDeleteCascadeAdminNegative(base.BaseVolumeAdminTest):

    @classmethod
    def skip_checks(cls):
        super(VolumesDeleteCascadeAdminNegative, cls).skip_checks()
        if not CONF.volume_feature_enabled.snapshot:
            raise cls.skipException("Cinder snapshot feature disabled")

    @decorators.idempotent_id('abcc0d5b-8f15-4ffb-aa75-717fe62733db')
    @testtools.skipIf(CONF.volume.storage_protocol == 'ceph',
                      'Skip because of Bug#1677525')
    def test_volume_delete_cascade_snapshot_error_deleting(self):
        # The test validates delete a volume when one of the snapshots
        # is not "available" or "error", such as "error_deleting"

        # Create a volume
        volume = self.create_volume()

        snapshot_list = []
        for _ in range(2):
            snapshot = self.create_snapshot(volume['id'])
            snapshot_list.append(snapshot)

        # Reset snapshot status to error_deleting
        self.admin_snapshots_client.reset_snapshot_status(
            snapshot_list[0]['id'], 'error_deleting')
        self.addCleanup(self.admin_snapshots_client.reset_snapshot_status,
                        snapshot_list[0]['id'], 'available')
        snapshot_get = self.admin_snapshots_client.show_snapshot(
            snapshot_list[0]['id'])['snapshot']
        self.assertEqual('error_deleting', snapshot_get['status'])

        # Try delete the parent volume with associated snapshots
        self.assertRaises(lib_exc.BadRequest,
                          self.volumes_client.delete_volume,
                          volume['id'], cascade=True)
