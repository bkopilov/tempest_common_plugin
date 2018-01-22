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

import os

from tempest.lib.common.utils import data_utils

from tempest_common_plugin.common.restartability.restartability import RestartManager


class Crudini(object):

    def __init__(self, ssh_client_list, config_file, backup_file=False,
                 docker_container_name=None, service_name=None):

        self.ssh_client_list = ssh_client_list
        self.config_file = config_file
        self.directory_path = os.path.dirname(config_file)
        self.directory_name = (self.directory_path.replace("/", "_")
                               + data_utils.rand_name("bk"))
        self.docker_container_name = docker_container_name
        self.service_name = service_name
        if backup_file:
            self._copy_config_to_temp(config_file)

    def _crudini_install(self):
        for ssh_client in self.ssh_client_list:
            ssh_client.run_command("sudo sudo yum install -y crudini")

    def _copy_config_to_temp(self, config_file):
        for ssh_client in self.ssh_client_list:
            ssh_client.run_command(
                'sudo /bin/cp -rfp --preserve=context {0} /tmp'
                .format(config_file))

    def backup_node_config(self):
        for ssh_client in self.ssh_client_list:
            ssh_client.run_command(
                "sudo tar cvzf /tmp/{0}.tar.gz {1}".format(
                    self.directory_name, self.directory_path))

    def recover_node_config(self, restart=True):
        for ssh_client in self.ssh_client_list:
            ssh_client.run_command(
                "sudo rm -rf {0} && sudo tar xzf "
                "/tmp/{1}.tar.gz -C /".format(self.directory_path,
                                              self.directory_name))
            ssh_client.run_command(
                "sudo rm -rf /tmp/{0}.tar.gz".format(self.directory_name))

        if restart:
                service = RestartManager(
                    ssh_clients=self.ssh_client_list,
                    docker_container_name=self.docker_container_name,
                    service_name=self.service_name)
                service.restart()

    def recover_config_file(self, service_name_restart=None,
                            process_name_signal=None):
        for ssh_client in self.ssh_client_list:
            ssh_client.run_command(
                'sudo mv /tmp/{0} {1}'.format(os.path.basename(
                    self.config_file), self.config_file))
            service = RestartManager(
                ssh_clients=self.ssh_client_list,
                docker_container_name=self.docker_container_name,
                service_name=service_name_restart)
        if service_name_restart:
            service.restart()
        if process_name_signal:
            service.send_signal_to_process(self.ssh_client_list,
                                           process_name_signal)

    def crudini_get(self, section, param="", format=None, ssh_client=None):
        """This method return the variable value in the given file reside on

        Example:
        crudini --format=ini --get /etc/tempest/tempest.conf compute flavor_ref
        returned from command : flavor_ref = 1
        :param section The section in ini file [xxx]
        :param param The param inside the section
        """
        command = 'sudo crudini --get {0} {1} {2} {3}'.\
            format("--format " + format if format else "",
                   self.config_file, section, param)

        ssh_client = ssh_client or self.ssh_client_list[0]
        output = ssh_client.run_command(
            command).rstrip()
        return str(output)

    def crudini_set(self, section, param_dict, check_existing=False):
        """This method set multiple variable value in the given file

        :param section: The section in ini file [xxx]
        :param param_dict: a dictionary of all values for a key
        :param check_existing: check if the section , param exists
                          raise exception if does not exist
        :return:
        """

        for param, value in param_dict.items():

            command = 'sudo crudini --set {0} {1} {2} {3} {4}'.format(
                "--existing" if check_existing else "",  self.config_file,
                section, param, "'" + str(value) + "'")

            for ssh_client in self.ssh_client_list:
                ssh_client.run_command(command)

    def crudini_delete(self, section, param_dict, check_existing=False):
        """This method deletes variable value in the given file

        :param section:
        :param param_dict:
        :param check_existing:
        :return:
        """
        for param, value in param_dict.items():
            command = 'sudo crudini {0} --del {1} {2} {3}' \
                .format("--existing" if check_existing else "",
                        self.config_file, section, param)
            for ssh_client in self.ssh_client_list:
                ssh_client.run_command(command)
