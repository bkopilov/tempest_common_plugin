
from tempest import config

import tempest_common_plugin.tests.lib.services.image.v2.\
    tasks_client as tasks_client

CONF = config.CONF


class Manager(object):
    def __init__(self, base_manager):
        self.base_manager = base_manager
        self._setup_image_clients()
        self._setup_volume_clients()

    def _setup_image_clients(self):
        params = {
            'service': CONF.image.catalog_type,
            'region': CONF.image.region,
            'endpoint_type': CONF.image.endpoint_type,
            'build_interval': CONF.image.build_interval,
            'build_timeout': CONF.image.build_timeout
        }
        params.update(self.base_manager.default_params)
        auth_provider = self.base_manager.auth_provider
        # init new clients
        self.task_client = tasks_client.TaskClient(auth_provider,
                                                   **params)

    def _setup_volume_clients(self):
        params = {
            'service': CONF.volume.catalog_type,
            'region': CONF.volume.region,
            'endpoint_type': CONF.volume.endpoint_type,
            'build_interval': CONF.volume.build_interval,
            'build_timeout': CONF.volume.build_timeout
        }
        # auth_provider = self.base_manager.auth_provider
