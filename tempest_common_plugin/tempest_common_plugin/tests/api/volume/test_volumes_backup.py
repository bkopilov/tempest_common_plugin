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


class VolumesBackupsTest(base.BaseVolumeTest):

    @classmethod
    def skip_checks(cls):
        super(VolumesBackupsTest, cls).skip_checks()
        if not CONF.volume_feature_enabled.backup:
            raise cls.skipException("Cinder backup feature disabled")

    def _delete_backup(self, backup_id):
        self.backups_client.delete_backup(backup_id)
        self.backups_client.wait_for_resource_deletion(backup_id)

    @decorators.idempotent_id('f86eff09-2a6d-43c1-905e-8079e5754f1e')
    def test_volume_backup_incremental(self):
        # Create a volume
        volume = self.create_volume()

        # Create a server
        server = self.create_server()

        # Attach volume to the server
        self.attach_volume(server['id'], volume['id'])

        # Create a backup to the attached volume
        backup1 = self.create_backup(volume['id'], force=True)

        # Validate backup details
        backup_info = self.backups_client.show_backup(backup1['id'])['backup']
        self.assertEqual(False, backup_info['has_dependent_backups'])
        self.assertEqual(False, backup_info['is_incremental'])

        # Create an incremental backup
        backup2 = self.backups_client.create_backup(
            volume_id=volume['id'], incremental='true', force=True)['backup']
        self.addCleanup(self._delete_backup, backup2['id'])
        waiters.wait_for_volume_resource_status(self.backups_client,
                                                backup2['id'], 'available')

        # Validate incremental backup details
        backup2_info = self.backups_client.show_backup(backup2['id'])['backup']
        self.assertEqual(True, backup2_info['is_incremental'])
        self.assertEqual(False, backup2_info['has_dependent_backups'])

        # Verify that the parent backup has a dependent backup
        backup_info = self.backups_client.show_backup(backup1['id'])['backup']
        self.assertEqual(True, backup_info['has_dependent_backups'])

        # Create another incremental backup
        backup3 = self.backups_client.create_backup(
            volume_id=volume['id'], incremental='true', force=True)['backup']
        waiters.wait_for_volume_resource_status(self.backups_client,
                                                backup3['id'], 'available')

        # Validate incremental backup details
        backup3_info = self.backups_client.show_backup(backup3['id'])['backup']
        self.assertEqual(True, backup3_info['is_incremental'])
        self.assertEqual(False, backup3_info['has_dependent_backups'])

        # Verify that the parent backup has a dependent backup
        backup2_info = self.backups_client.show_backup(backup2['id'])['backup']
        self.assertEqual(True, backup2_info['has_dependent_backups'])

        # Delete the last incremental backup that was created
        self.backups_client.delete_backup(backup3['id'])
        self.backups_client.wait_for_resource_deletion(backup3['id'])

        # Create another incremental backup
        backup4 = self.backups_client.create_backup(
            volume_id=volume['id'], incremental='true', force=True)['backup']
        self.addCleanup(self._delete_backup, backup4['id'])
        waiters.wait_for_volume_resource_status(self.backups_client,
                                                backup4['id'], 'available')

        # Validate incremental backup details
        backup4_info = self.backups_client.show_backup(backup4['id'])['backup']
        self.assertEqual(True, backup4_info['is_incremental'])
        self.assertEqual(False, backup4_info['has_dependent_backups'])
