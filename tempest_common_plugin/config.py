# Copyright 2016
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

from oslo_config import cfg

parallel_testing = cfg.OptGroup(name='parallel_testing',
                                     title="Options for parallel tests")
ParallelTesting = [
    cfg.IntOpt('total_volumes',
               default=2,
               help="create volumes in parallel"),
]

prepare_cloud_group = cfg.OptGroup(name='prepare_cloud_setup',
                                        title="Options for cloud setup")

PrepareCloudGroup = [
    cfg.StrOpt('store_json_before',
               default='/home/stack/test_before.json',
               help="store cloud objects per client before actions"),
    cfg.StrOpt('store_json_after',
               default='/home/stack/test_after.json',
               help="store cloud objects per client after actions"),
    cfg.IntOpt('volumes_create',
               default=1,
               help="create volumes from image with data"),
]


ssh_authentication_group = cfg.OptGroup(name='ssh_credentials',
                                        title="Options for authentication "
                                              "and credentials")

SshAuthenticationGroup = [
    cfg.StrOpt('user',
               default='heat-admin',
               help="ssh user authentication for login to host"),
    cfg.StrOpt('password',
               default=None,
               help="ssh password authentication for login to host"),
    cfg.BoolOpt('look_for_keys',
                default=True,
                help="Look for private key in ~/.ssh/"),
    cfg.StrOpt('key_filename',
               default=None,
               help="ssh private key file location")
]

