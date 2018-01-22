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
import time

from oslo_log import log

import tempest.lib.exceptions as excetpions

from tempest.lib.common import ssh

LOG = log.getLogger(__name__)


class RemoteClient(ssh.Client):

    def __init__(self, ip_address, username, password=None,
                 look_for_keys=True, key_filename=None, pkey=None, port=22):
        """Executes commands in a VM over ssh

               :param ip_address: IP address to ssh to
               :param username: ssh username
               :param password: ssh password (optional)
               :param pkey: ssh public key (optional)
               :param look_for_keys  Whether or not to search for private keys
                      in ``~/.ssh``.  Default is False.
               :param key_filename private_key file
               :param pkey private_key file

               Authentication order:
                - The ``pkey`` or ``key_filename`` passed in (if any)
                - Any key we can find through an SSH agent
                - Any "id_rsa", "id_dsa" or "id_ecdsa" key discoverable in
              ``~/.ssh/``
            - Plain username/password auth, if a password was given

        """
        super(RemoteClient, self).__init__(
            ip_address, username, password=password,
            look_for_keys=look_for_keys, key_filename=key_filename, pkey=pkey,
            port=port)

    def run_command(self, cmd, expected_failure_message=None,
                    sleep_after_command=0):
        try:
            LOG.info("=== {0} ===".format(0))
            cmd = self.exec_command(cmd)
            time.sleep(sleep_after_command)
            return cmd
        except excetpions.SSHExecCommandFailed as e:
            if expected_failure_message and expected_failure_message \
                    in e._error_string:
                pass
            else:
                raise e
