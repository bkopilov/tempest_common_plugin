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

from tempest.common import waiters
from tempest import config
from tempest.lib import decorators
from tempest.lib import exceptions

from tempest_common_plugin.tests.api.volume import base

CONF = config.CONF


class SnapshotManageAdminTest(base.BaseVolumeAdminTest):

    @classmethod
    def skip_checks(cls):
        super(SnapshotManageAdminTest, cls).skip_checks()

        if not CONF.volume_feature_enabled.manage_snapshot:
            raise cls.skipException("Manage snapshot tests are disabled")

        if len(CONF.volume.manage_snapshot_ref) != 2:
            msg = ("Manage snapshot ref is not correctly configured, "
                   "it should be a list of two elements")
            raise exceptions.InvalidConfiguration(msg)

    def manage_snapshot(self, volume_id, snapshot_id, name=None,
                        description=None, metadata=None):

        # Verify the original snapshot does not exist in snapshot list
        params = {'all_tenants': 1}
        all_snapshots = self.admin_snapshots_client.list_snapshots(
            detail=True, params=params)['snapshots']
        self.assertNotIn(snapshot_id, [v['id'] for v in all_snapshots])

        snapshot_ref = {
            'volume_id': volume_id,
            'ref': {CONF.volume.manage_snapshot_ref[0]:
                    CONF.volume.manage_snapshot_ref[1] % snapshot_id},
            'name': name,
            'description': description,
            'metadata': metadata
        }
        new_snapshot = self.admin_snapshot_manage_client.manage_snapshot(
            **snapshot_ref)['snapshot']
        self.addCleanup(self.delete_snapshot, new_snapshot['id'],
                        self.admin_snapshots_client)
        # Wait for the snapshot to be available after manage operation
        waiters.wait_for_volume_resource_status(self.admin_snapshots_client,
                                                new_snapshot['id'],
                                                'available')
        return new_snapshot

    @decorators.idempotent_id('7c735385-e953-4198-8534-68137f72dbdc')
    def test_snapshot_manage_with_attached_volume(self):
        """Test manage a snapshot with an attached volume.

           The case validates manage snapshot operation while
           the parent volume is attached to an instance.
        """
        # Create a volume
        volume = self.create_volume()

        # Create a snapshot
        snapshot = self.create_snapshot(volume_id=volume['id'])

        # Create a server
        server = self.create_server()

        # Attach volume to instance
        self.attach_volume(server['id'], volume['id'])

        # Unmanage the snapshot
        self.admin_snapshots_client.unmanage_snapshot(snapshot['id'])
        self.admin_snapshots_client.wait_for_resource_deletion(snapshot['id'])

        # Manage the snapshot
        new_snapshot = self.manage_snapshot(volume['id'], snapshot['id'])
        self.assertEqual(new_snapshot['volume_id'], volume['id'])
