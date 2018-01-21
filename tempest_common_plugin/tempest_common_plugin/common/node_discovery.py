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

import re

from collections import defaultdict

from tempest_common_plugin.common.utils.linux.remote_client \
    import RemoteClient


class NodeOvercloudDiscovery(object):
    """Node discovery

    :param undercloud_ip:
    :param undercloud_user:
    :param undercloud_pass:
    :return: a dictionary of all service
    Example:  {"openstack-cinder":[
    {"ip":"192.168.1.1", "load": xxx, active: xxx, sub:xxx, description:yyy}
    {"ip":"192.168.1.2", "load": xxx, active: xxx, sub:xxx, description:yyy}
    {"ip":"192.168.1.3", "load": xxx, active: xxx, sub:xxx, description:yyy}
    ]
    if its container base instal - rhos12 and above:
    Example:  {"swift_proxy":[
    {"ip":"192.168.1.1", "container_id": xxx, image: xxx, status:yyy}
    {"ip":"192.168.1.2", "container_id": xxx, image: xxx, status:yyy}
    {"ip":"192.168.1.3", "container_id": xxx, image: xxx, status:yyy}
    ]
    """

    def __init__(self, undercloud_ip="127.0.0.1", undercloud_user="stack",
                 undercloud_pass="stack", docker_install=True):
        self.store_nodes = defaultdict(list)
        self.nodes = self._get_nodes_list(undercloud_ip, undercloud_user,
                                          undercloud_pass)
        self.docker_install = docker_install
        self._set_services_info()

    @staticmethod
    def _get_nodes_list(undercloud_ip, undercloud_user,
                        undercloud_pass):
        ssh_client = RemoteClient(
            ip_address=undercloud_ip, username=undercloud_user,
            password=undercloud_pass, port=22, look_for_keys=False)
        nodes = list()
        ip = ssh_client.run_command(
            "source ~/stackrc && nova list | grep ACTIVE | grep -v ceph|"
            " grep Running|"
            " awk '{print$4, $12}'")
        for line in ip.split('\n'):
            if line:
                virsh_type = line.split(" ")[0]
                node_ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
                                     line)
                nodes.append({"ip": "".join(node_ip),
                              "virsh_type": virsh_type})
        if not nodes:
            raise RuntimeError("Unable to find nodes")
        return nodes

    def _add_to_dictionaty(self, line_raw, node, virsh_type):
        line_info = line_raw.split()
        service_name = line_info[0]
        kwargs = {"ip": node,
                  "vm_type": virsh_type,
                  "load": line_info[1],
                  "active": line_info[2],
                  "sub": line_info[3], "description":
                  " ".join(line_info[4::])}
        self.store_nodes[service_name].append(kwargs)

    def _add_docker_to_dictionaty(self, line_raw, node, virsh_type):
        line_info = line_raw.split()
        docker_name = line_info[0]
        kwargs = {"ip": node,
                  "virsh_type": virsh_type,
                  "container_id": line_info[1],
                  "image": line_info[2],
                  "status":
                  " ".join(line_info[3::])}
        self.store_nodes[docker_name].append(kwargs)

    def _get_openstack_services(self, node):
        c = RemoteClient(
            ip_address=node, username="heat-admin",
            port=22, look_for_keys=True)
        # get all openstack services
        if self.docker_install is False:
            return c.run_command(
                "sudo systemctl -a | grep openstack | grep -v ^$")
        else:
            cmd = c.run_command(
                """sudo docker ps -a --format \
                "{{.Names}} {{.ID}} {{.Image}} {{.Status}}" | grep -v ^$""")
            return cmd

    def _set_services_info(self):
        for node in self.nodes:
            output = self._get_openstack_services(node['ip'])
            split_by_raws = output.rstrip().split('\n')
            func = self._add_docker_to_dictionaty\
                if self.docker_install else self._add_to_dictionaty
            for line_raw in split_by_raws:
                func(line_raw, node['ip'], node['virsh_type'])

    def get_nodes_by_service(self, service_name):
        if self.store_nodes.get(service_name):
            return [node['ip'] for node in self.store_nodes[service_name]]
        raise RuntimeError("Can not find any node under service name %s"
                           % service_name)

    def get_service_by_node(self, node_ip, service_name):
        if self.store_nodes.get(service_name):
            for node in self.store_nodes[service_name]:
                if node['ip'] == node_ip:
                    return node['ip']

    def get_nodes_by_container(self, container_name):
        if self.store_nodes.get(container_name):
            return [node['ip'] for node in self.store_nodes[container_name]]
        raise RuntimeError("Can not find any node under service name %s"
                           % container_name)

    def get_nodes_info_by_container(self, container_name):
        if self.store_nodes.get(container_name):
            return self.store_nodes[container_name]
        raise RuntimeError("Can not find any node under service name %s"
                           % container_name)

    def get_container_by_node(self, node_ip, container_name):
        if self.store_nodes.get(container_name):
            for node in self.store_nodes[container_name]:
                if node['ip'] == node_ip:
                    return node['ip']

    def get_stored_nodes(self):
        return self.store_nodes
