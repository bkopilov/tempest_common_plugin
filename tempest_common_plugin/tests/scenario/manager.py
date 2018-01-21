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

from tempest.lib.common.utils import data_utils

from tempest.scenario import manager as scenario_tempest_manager

import tempest_common_plugin.tests.clients as client

CONF = config.CONF


class ScenarioTest(scenario_tempest_manager.ScenarioTest):

    credentials = ['primary', "admin"]

    @classmethod
    def skip_checks(cls):
        super(ScenarioTest, cls).skip_checks()

    @classmethod
    def setup_clients(cls):
        super(ScenarioTest, cls).setup_clients()
        cls.backups_client = cls.os_primary.backups_v2_client
        manager = client.Manager(cls.os_admin)
        cls.admin_task_client = manager.task_client
        cls.admin_image_client = cls.os_admin.image_client_v2

    def remove_from_cleanup(self, key_id):
        to_remove = [elem for elem in self._cleanups if key_id in elem[1]]
        map(lambda x: self._cleanups.remove(x), to_remove)

    def create_backup(self, volume_id, name=None, description=None,
                      force=False, snapshot_id=None, incremental=False,
                      container=None):
        name = name or data_utils.rand_name(
            self.__class__.__name__ + "-backup")
        kwargs = {'name': name,
                  'description': description,
                  'force': force,
                  'snapshot_id': snapshot_id,
                  'incremental': incremental,
                  'container': container}
        backup = self.backups_client.create_backup(volume_id=volume_id,
                                                   **kwargs)['backup']
        self.addCleanup(self.backups_client.delete_backup, backup['id'])
        waiters.wait_for_volume_resource_status(self.backups_client,
                                                backup['id'], 'available')
        return backup

    def restore_backup(self, backup_id, volume=None):
        restore = self.backups_client.restore_backup(backup_id,
                                                     volume=volume)['restore']
        self.addCleanup(self.volumes_client.delete_volume,
                        restore['volume_id'])
        waiters.wait_for_volume_resource_status(self.backups_client,
                                                backup_id, 'available')
        waiters.wait_for_volume_resource_status(self.volumes_client,
                                                restore['volume_id'],
                                                'available')
        self.assertEqual(backup_id, restore['backup_id'])
        return restore

    def create_md5_from_file(self, ip_address, dev_name=None,
                             mount_path='/mnt', private_key=None,
                             file_name="timestamp"):
        ssh_client = self.get_remote_client(ip_address,
                                            private_key=private_key)
        if dev_name is not None:
            ssh_client.make_fs(dev_name)
            ssh_client.exec_command('sudo mount /dev/%s %s' % (dev_name,
                                                               mount_path))
        cmd_timestamp = 'sudo sh -c "date > %s/%s; sync"' %\
                        (mount_path, file_name)
        ssh_client.exec_command(cmd_timestamp)
        md5 = ssh_client.exec_command(
            'sudo md5sum %s/%s|cut -c 1-32' % (mount_path, file_name))
        if dev_name is not None:
            ssh_client.exec_command('sudo umount %s' % mount_path)
        return md5

    def get_md5_from_file(self, ip_address, dev_name=None, mount_path='/mnt',
                          private_key=None, file_name="timestamp"):
        ssh_client = self.get_remote_client(ip_address,
                                            private_key=private_key)
        if dev_name is not None:
            ssh_client.mount(dev_name, mount_path)
        md5 = ssh_client.exec_command('sudo md5sum %s/%s|cut -c 1-32'
                                      % (mount_path, file_name))
        if dev_name is not None:
            ssh_client.exec_command('sudo umount %s' % mount_path)
        return md5


class NetworkScenarioTest(scenario_tempest_manager.NetworkScenarioTest):
    @classmethod
    def setup_clients(cls):
        super(NetworkScenarioTest, cls).setup_clients()

    @classmethod
    def skip_checks(cls):
        super(NetworkScenarioTest, cls).skip_checks()


class EncryptionScenarioTest(scenario_tempest_manager.EncryptionScenarioTest):
    @classmethod
    def setup_clients(cls):
        super(EncryptionScenarioTest, cls).setup_clients()

    @classmethod
    def skip_checks(cls):
        super(EncryptionScenarioTest, cls).skip_checks()

    def create_encrypted_volume(self, encryption_provider, volume_type,
                                imageRef=None, key_size=256,
                                cipher='aes-xts-plain64',
                                control_location='front-end'):
        volume_type = self.create_volume_type(name=volume_type)
        self.create_encryption_type(type_id=volume_type['id'],
                                    provider=encryption_provider,
                                    key_size=key_size,
                                    cipher=cipher,
                                    control_location=control_location)
        return self.create_volume(volume_type=volume_type['name'],
                                  imageRef=imageRef)


class ObjectStorageScenarioTest(scenario_tempest_manager.
                                ObjectStorageScenarioTest):
    @classmethod
    def setup_clients(cls):
        super(ObjectStorageScenarioTest, cls).setup_clients()

    @classmethod
    def skip_checks(cls):
        super(ObjectStorageScenarioTest, cls).skip_checks()


class QosSpecsScenarioTest(scenario_tempest_manager.ScenarioTest):

    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(QosSpecsScenarioTest, cls).setup_clients()
        cls.admin_volume_qos_client = cls.os_admin.volume_qos_v2_client

    @classmethod
    def skip_checks(cls):
        super(QosSpecsScenarioTest, cls).skip_checks()

    def create_test_qos_specs(self, name=None, consumer=None, **kwargs):
        """create a test Qos-Specs."""
        name = name or data_utils.rand_name(self.__class__.__name__ + '-QoS')
        consumer = consumer or 'front-end'
        qos_specs = self.admin_volume_qos_client.create_qos(
            name=name, consumer=consumer, **kwargs)['qos_specs']
        self.addCleanup(
            self.admin_volume_qos_client.wait_for_resource_deletion,
            qos_specs['id'])
        self.addCleanup(self.admin_volume_qos_client.delete_qos,
                        qos_specs['id'])
        return qos_specs

    def associate_qos(self, qos_id, vol_type_id):
        self.admin_volume_qos_client.associate_qos(
            qos_id, vol_type_id)
        operation = 'disassociate'
        self.addCleanup(waiters.wait_for_qos_operations,
                        self.admin_volume_qos_client, qos_id, operation)
        self.addCleanup(self.admin_volume_qos_client.disassociate_qos, qos_id,
                        vol_type_id)
