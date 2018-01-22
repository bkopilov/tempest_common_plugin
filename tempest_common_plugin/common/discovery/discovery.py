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

from tempest_common_plugin.common.remote_client.ssh_client \
    import RemoteClient


class DiscoveryManager(object):
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
                 undercloud_pass="stack"):
        self.store_nodes = defaultdict(list)
        self.nodes = self._get_nodes_list(undercloud_ip, undercloud_user,
                                          undercloud_pass)

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

    def get_stored_nodes(self):
        return self.store_nodes

