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

import six

from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib import decorators

from tempest_common_plugin.tests.api.image import base

CONF = config.CONF


class ImagesActionsTest(base.BaseV2ImageAdminTest):

    @decorators.idempotent_id('f6ab4aa0-035e-4664-9f2d-c57c6df50605')
    def test_admin_list_public_image(self):
        """Create new public image and check if others can access .

        Create a public image
        Make sure that a none admin user can access this image.
        """
        # Create a public image
        image_file = six.BytesIO(data_utils.random_bytes(2048))
        container_format = CONF.image.container_formats[0]
        disk_format = CONF.image.disk_formats[0]
        name = data_utils.rand_name(self.__class__.__name__ + '-Image')
        image = self.admin_client.create_image(
            name=name,
            container_format=container_format,
            visibility='public',
            disk_format=disk_format)
        self.addCleanup(self.admin_client.delete_image, image['id'])
        self.admin_client.store_image_file(image['id'], data=image_file)

        # As an image consumer you need to provide the member_status parameter
        # along with the visibility=public parameter in order for it to show
        # results
        params = {'member_status': 'pending', 'visibility': 'public'}
        fetched_images = self.client.list_images(params)['images']
        self.assertEqual(image['id'], fetched_images[0]['id'])
