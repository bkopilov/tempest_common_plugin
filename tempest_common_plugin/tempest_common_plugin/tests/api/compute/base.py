import tempest.api.compute.base as base_tempest_compute


class BaseV2ComputeTest(base_tempest_compute.BaseV2ComputeTest):
    @classmethod
    def skip_checks(cls):
        super(BaseV2ComputeTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseV2ComputeTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV2ComputeTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV2ComputeTest, cls).resource_setup()


class BaseV2ComputeAdminTest(base_tempest_compute.BaseV2ComputeTest):
    @classmethod
    def skip_checks(cls):
        super(BaseV2ComputeAdminTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseV2ComputeAdminTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV2ComputeAdminTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV2ComputeAdminTest, cls).resource_setup()
