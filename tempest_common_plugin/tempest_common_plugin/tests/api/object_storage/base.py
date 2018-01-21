import tempest.api.object_storage.base as base_tempest_object_storage


class BaseObjectTest(base_tempest_object_storage.BaseObjectTest):

    @classmethod
    def skip_checks(cls):
        super(BaseObjectTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseObjectTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseObjectTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseObjectTest, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(BaseObjectTest, cls).resource_cleanup()
