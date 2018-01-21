
import tempest.api.volume.base as base_tempest_volume


class BaseVolumeTest(base_tempest_volume.BaseVolumeTest):
    @classmethod
    def skip_checks(cls):
        super(BaseVolumeTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseVolumeTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseVolumeTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseVolumeTest, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(BaseVolumeTest, cls).resource_cleanup()


class BaseVolumeAdminTest(base_tempest_volume.BaseVolumeAdminTest):
    @classmethod
    def skip_checks(cls):
        super(BaseVolumeAdminTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseVolumeAdminTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseVolumeAdminTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseVolumeAdminTest, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(BaseVolumeAdminTest, cls).resource_cleanup()
