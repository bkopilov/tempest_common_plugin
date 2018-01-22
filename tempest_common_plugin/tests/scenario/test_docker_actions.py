from tempest import config

from tempest.lib import decorators

from tempest_common_plugin.common.discovery.docker_discovery import \
    DockerDiscovery

from tempest_common_plugin.common.high_availability.\
     restartability import RestartManager

from tempest_common_plugin.common.remote_client.ssh_client \
    import RemoteClient
from tempest_common_plugin.tests.scenario import manager

CONF = config.CONF


class TestGlanceImageApiDockerBasicActions(manager.ScenarioTest,
                                           manager.ObjectStorageScenarioTest):
    credentials = ['primary', 'admin']
    docker_name = "glance_api"

    @classmethod
    def resource_setup(cls):
        super(TestGlanceImageApiDockerBasicActions, cls).resource_setup()
        cls.nodes_info = DockerDiscovery()
        ip_list = cls.nodes_info.get_nodes_by_name(cls.docker_name)
        cls.ssh_clients = []
        kwargs = {"username": CONF.ssh_credentials.user,
                  "password": CONF.ssh_credentials.password,
                  "look_for_keys": CONF.ssh_credentials.look_for_keys}
        for ssh_ip in ip_list:
            cls.ssh_clients.append(RemoteClient(ip_address=ssh_ip,
                                                **kwargs))

    def _before_docker_state_change(self):
        self.server_info = self.create_server()
        self.volume_info = self.create_volume()
        self.container_name = self.create_container()
        self.obj_name, obj_data = self.upload_object_to_container(
            self.container_name)
        self.list_and_check_container_objects(self.container_name,
                                              present_obj=[self.obj_name])
        # self.glance_image = self.glance_image_create()

    @decorators.idempotent_id('86a0696f-fb26-4cfc-b7d3-fce1ea03d0f0')
    def test_docker_restart_and_wait_till_up(self):
        # verify dockers are up before test
        all_nodes = self.nodes_info.get_nodes_info_by_name(
            self.docker_name)
        stat_all_nodes = list(map(lambda x: x['status'], all_nodes))
        map((lambda stat: self.assertIn("Up", stat)), stat_all_nodes)
        self._before_docker_state_change()
        service_manager = RestartManager(
            self.ssh_clients, docker_container_name=self.docker_name)
        service_manager.restart()
        # verify that docker id was not changed

    @decorators.idempotent_id('8f066a3e-0819-4226-9bac-634c57aec81d')
    def test_docker_stop_start_wait_till_up(self):
        # verify dockers are up before test
        all_nodes = self.nodes_info.get_nodes_info_by_name(
            self.docker_name)
        stat_all_nodes = list(map(lambda x: x['status'], all_nodes))
        map((lambda stat: self.assertIn("Up", stat)), stat_all_nodes)
        self._before_docker_state_change()
        service_manager = RestartManager(
            self.ssh_clients, docker_container_name=self.docker_name)
        service_manager.stop()
        service_manager.start()


class TestSwiftDockerBasicActions(TestGlanceImageApiDockerBasicActions):
    credentials = ['primary', 'admin']
    docker_name = "swift_proxy"


class TestNovaComputeDockerBasicActions(TestGlanceImageApiDockerBasicActions):
    credentials = ['primary', 'admin']
    docker_name = "nova_compute"
