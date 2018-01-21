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

from tempest_common_plugin.tests.api.volume import base

CONF = config.CONF


class VolumeRetypeTest(base.BaseVolumeAdminTest):

    @classmethod
    def skip_checks(cls):
        super(VolumeRetypeTest, cls).skip_checks()

        if not CONF.volume_feature_enabled.multi_backend:
            raise cls.skipException("Cinder multi-backend feature disabled.")

        if len(set(CONF.volume.backend_names)) < 2:
            raise cls.skipException("Requires at least two different "
                                    "backend names")

    @classmethod
    def resource_setup(cls):
        super(VolumeRetypeTest, cls).resource_setup()
        # read backend name from a list.
        backend_src = CONF.volume.backend_names[0]
        backend_dst = CONF.volume.backend_names[1]

        extra_specs_src = {"volume_backend_name": backend_src}
        extra_specs_dst = {"volume_backend_name": backend_dst}

        cls.src_vol_type = cls.create_volume_type(extra_specs=extra_specs_src)
        cls.dst_vol_type = cls.create_volume_type(extra_specs=extra_specs_dst)

    @decorators.idempotent_id('ac3d3383-cd62-4c5e-99e9-bb4b00a9faaa')
    def test_volume_retype_deleted_snapshot(self):
        # Create a volume
        src_vol = self.create_volume(volume_type=self.src_vol_type['name'])

        # Create a volume snapshot
        snapshot = self.create_snapshot(src_vol['id'])

        # Create a volume from the snapshot
        vol_from_snap = self.create_volume(snapshot_id=snapshot['id'])

        # Delete the snapshot
        self.snapshots_client.delete_snapshot(snapshot['id'])
        self.snapshots_client.wait_for_resource_deletion(snapshot['id'])

        keys_with_no_change = ('id', 'size', 'description', 'name', 'user_id',
                               'os-vol-tenant-attr:tenant_id')

        keys_with_change = ('volume_type', 'os-vol-host-attr:host')
        volume_source = self.admin_volume_client.show_volume(
            vol_from_snap['id'])['volume']

        # Migrate volume from backend_src to backend_dst
        self.volumes_client.retype_volume(vol_from_snap['id'],
                                          new_type=self.dst_vol_type['name'],
                                          migration_policy='on-demand')
        waiters.wait_for_volume_retype(self.volumes_client,
                                       vol_from_snap['id'],
                                       self.dst_vol_type['name'])

        # Check the volume information after the migration.
        volume_dest = self.admin_volume_client.show_volume(
            vol_from_snap['id'])['volume']
        self.assertEqual('success',
                         volume_dest['os-vol-mig-status-attr:migstat'])
        self.assertEqual('success', volume_dest['migration_status'])

        for key in keys_with_no_change:
            self.assertEqual(volume_source[key], volume_dest[key])

        for key in keys_with_change:
            self.assertNotEqual(volume_source[key], volume_dest[key])
