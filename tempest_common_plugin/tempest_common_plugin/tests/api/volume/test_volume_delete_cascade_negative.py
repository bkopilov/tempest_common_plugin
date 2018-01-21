# Copyright 2016 Red Hat, Inc.
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


class VolumesDeleteCascadeNegative(base.BaseVolumeTest):

    @classmethod
    def skip_checks(cls):
        super(VolumesDeleteCascadeNegative, cls).skip_checks()
        if not CONF.volume_feature_enabled.snapshot:
            raise cls.skipException("Cinder snapshot feature disabled")

    @decorators.idempotent_id('83e61d7e-f829-4c96-a16b-091961dce225')
    @testtools.skipIf(CONF.volume.storage_protocol == 'ceph',
                      'Skip because of Bug#1677525')
    def test_volume_delete_cascade_attached_volume(self):
        # The case validates delete a volume with associated snapshots
        # while the volume is attached to a server.

        # Create a volume
        volume = self.create_volume()

        for _ in range(2):
            self.create_snapshot(volume['id'])

        # Create a server and attach it to the volume parent
        server = self.create_server()
        self.attach_volume(server['id'], volume['id'])

        #  Try to delete the patent volume
        self.assertRaises(lib_exc.BadRequest,
                          self.volumes_client.delete_volume, volume['id'],
                          cascade=True)
