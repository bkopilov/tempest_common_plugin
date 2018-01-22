
from discovery import DiscoveryManager
from tempest_common_plugin.common.remote_client.ssh.remote_client \
    import RemoteClient


class DockerDiscovery(DiscoveryManager):

        CMD = """sudo docker ps -a --format \
                "{{.Names}} {{.ID}} {{.Image}} {{.Status}}" | grep -v ^$"""

        def __init__(self, undercloud_ip="127.0.0.1", undercloud_user="stack",
                     undercloud_pass="stack"):
            super(DockerDiscovery, self).__init__(
                undercloud_ip=undercloud_ip, undercloud_user=undercloud_user,
                undercloud_pass=undercloud_pass)
            self._set_docker_info()

        def _get_openstack_command_output(self, node):
            c = RemoteClient(
                ip_address=node, username="heat-admin",
                port=22, look_for_keys=True)
            cmd = c.run_command(self.CMD)
            return cmd

        def _set_docker_info(self):
            for node in self.nodes:
                output = self._get_openstack_command_output(node['ip'])
                split_by_raws = output.rstrip().split('\n')
                for line_raw in split_by_raws:
                    self._add_to_dictionary(line_raw, node['ip'], node['virsh_type'])

        def _add_to_dictionary(self, line_raw, node, virsh_type):
            line_info = line_raw.split()
            docker_name = line_info[0]
            kwargs = {"ip": node,
                      "virsh_type": virsh_type,
                      "container_id": line_info[1],
                      "image": line_info[2],
                      "status":
                          " ".join(line_info[3::])}
            self.store_nodes[docker_name].append(kwargs)

        def get_nodes_by_name(self, name):
            if self.store_nodes.get(name):
                return [node['ip'] for node in self.store_nodes[name]]
            raise RuntimeError("Can not find any node under service name %s"
                               % name)

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

