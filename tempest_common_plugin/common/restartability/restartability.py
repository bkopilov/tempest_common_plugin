import time

import tempest_common_plugin.common.exceptions as \
    tempest_exception


class RestartManager(object):
    RETRY_COUNT = 20
    TIME_BETWEEN_RETRIES = 6

    def __init__(self, ssh_clients, docker_container_name=None,
                 service_name=None):
        """
        :param ssh_clients:
        :param docker_container_name:
        :param service_name:
        """
        self.ssh_clients = ssh_clients
        self.service_name = service_name
        self.docker_container_name = docker_container_name

    def status(self, ssh_client):
        """

        :param ssh_client:
        :return:
        """
        if self.service_name:
            status = ssh_client.run_command(
                "sudo systemctl is-active {0} ".format(
                    self.service_name)).strip()
        elif self.docker_container_name:
            docker_status = \
                """sudo docker ps -a --filter 'name={0}'| grep -v CONT"""\
                .format(self.docker_container_name)
            status = ssh_client.run_command(docker_status).strip()
        return str(status)

    def stop(self, ssh_client=[]):
        """

        :param ssh_client:
        :return:
        """
        if len(ssh_client) == 0:
            ssh_client = self.ssh_clients
        for ssh in ssh_client:
            if self.service_name:
                ssh.run_command("sudo systemctl stop {0}"
                                .format(self.service_name))
            elif self.docker_container_name:
                ssh.run_command("sudo docker stop {0}".format(
                    self.docker_container_name))
                self._wait_for_service_status(ssh, status="Exited")
            else:
                raise RuntimeError("Type is not value")

    def start(self, ssh_client=[]):
        """

        :param ssh_client:
        :return:
        """
        if len(ssh_client) == 0:
            ssh_client = self.ssh_clients
        for ssh in ssh_client:
            if self.service_name:
                ssh.run_command("sudo systemctl start {0}"
                                .format(self.service_name))
                self._wait_for_service_status(ssh_client, self.service_name)
            elif self.docker_container_name:
                ssh.run_command("sudo docker start {0}"
                                .format(self.docker_container_name))
                self._wait_for_service_status(ssh, status="Up")
            else:
                raise RuntimeError("Type is not valid")

    def restart(self, ssh_client=[], timeout_before_checking_status=5):
        """
        :param ssh_client:
        :param timeout_before_checking_status:
        :return:
        """
        if len(ssh_client) == 0:
            ssh_client = self.ssh_clients
        for ssh in ssh_client:
            if self.service_name:
                ssh.run_command("sudo systemctl restart {0}"
                                .format(self.service_name))
                time.sleep(timeout_before_checking_status)
                self._wait_for_service_status(ssh)
            elif self.docker_container_name:
                ssh.run_command("sudo docker restart {0}"
                                .format(self.docker_container_name))
                time.sleep(timeout_before_checking_status)
                self._wait_for_service_status(ssh, status="Up")
            else:
                raise RuntimeError("Type is not valid")

    def _wait_for_service_status(self, ssh_client, status="active"):
        retry_count = 0
        while retry_count < self.RETRY_COUNT:
            status_value = self.status(ssh_client)
            if status in status_value:
                return 1
            retry_count += 1
            time.sleep(self.TIME_BETWEEN_RETRIES)
        raise tempest_exception.ServiceRestartException()

    @classmethod
    def send_signal_to_process(cls, ssh_client, process_name, signal='SIGINT'):
        for ssh in ssh_client:
            ssh.run_command(
                "sudo ps aux | grep [%s]%s | awk '{print$2}' | "
                "sudo xargs -I {} kill -s %s {}" % (process_name[0],
                                                    process_name[1:],
                                                    signal))

    @classmethod
    def pcs_cluster_stop(cls, ssh_client, force=True, nodes="--all"):
        """cluster stop

        :param ssh_client:
        :param force: force stop , try by default
        :param nodes choose to stop all nodes or others
        """
        res = ssh_client.run_command("sudo pcs {0} cluster stop {1}".format(
            "--force " if force else "", nodes))
        return res

    @classmethod
    def pcs_cluster_start(cls, ssh_client, force=True, nodes="--all"):
        """cluster start

        :param ssh_client:
        :param force: force start , try by default
        :param nodes choose to start all nodes or others
        """
        res = ssh_client.run_command("sudo pcs {0} cluster start {1}".format(
            "--force " if force else "", nodes))
        return res
