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
from tempest.lib import decorators
from tempest.lib import exceptions as lib_exc

from tempest_common_plugin.tests.api.volume import base

CONF = config.CONF


class VolumesSnapshotNegativeTestJSON(base.BaseVolumeTest):

    @classmethod
    def skip_checks(cls):
        super(VolumesSnapshotNegativeTestJSON, cls).skip_checks()
        if not CONF.volume_feature_enabled.snapshot:
            raise cls.skipException("Cinder volume snapshots are disabled")

    @decorators.attr(type=['negative'])
    @decorators.idempotent_id('ad1b2fbe-7188-4dfd-8b39-c03778b07475')
    def test_delete_parent_volume_with_associated_snapshot(self):
        volume = self.create_volume()
        self.create_snapshot(volume_id=volume['id'])
        self.assertRaises(lib_exc.BadRequest,
                          self.volumes_client.delete_volume,
                          volume['id'])
