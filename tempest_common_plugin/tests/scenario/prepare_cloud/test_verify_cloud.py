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

from tempest_common_plugin.common.capture_cloud.compare_dictionary \
    import CompareDictionary
from tempest_common_plugin.common.capture_cloud.json_actions \
    import JsonManager
from tempest_common_plugin.tests.scenario import manager

CONF = config.CONF


class VerifyCloudActions(manager.ScenarioTest):
    """
    This class must run after test_prepare_cloud.
    We load old json and compare it with current clients status
    Once we have two json with dictionary data we run a compare between them
    In case one of the object is missing or changed we raise an assert
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
        super(VerifyCloudActions, cls).resource_setup()
        cls.restored_cloud_before = cls._load_from_json(
            CONF.prepare_cloud_setup.store_json_before, "r")

        cls.json_manager_after = JsonManager(
            file_location=CONF.prepare_cloud_setup.store_json_after,
            permission="w")
        cls.json_manager_after.capture_setup_by_clients(cls.os_admin)

        cls.restored_cloud_after = cls._load_from_json(
            CONF.prepare_cloud_setup.store_json_after, "r")

    @classmethod
    def resource_cleanup(cls):
        super(VerifyCloudActions, cls).resource_cleanup()

    @decorators.idempotent_id('c1418e8c-3179-4cc6-a306-f3a2058b69ba')
    def test_verify_attached_volumes_snapshots(self):
        a = self.restored_cloud_before
        b = self.restored_cloud_after
        cmp1 = CompareDictionary(a, b).compare_dictionaries()
        cmp1 = cmp1 if len(cmp1) else None
        self.assertIsNone(cmp1)
