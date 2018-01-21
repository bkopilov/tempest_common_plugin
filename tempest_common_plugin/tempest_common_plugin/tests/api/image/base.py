import tempest.api.image.base as base_tempest_image


class BaseImageTest(base_tempest_image.BaseImageTest):

    @classmethod
    def skip_checks(cls):
        super(BaseImageTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseImageTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseImageTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseImageTest, cls).resource_setup()


class BaseV1ImageTest(base_tempest_image.BaseV1ImageTest):
    @classmethod
    def skip_checks(cls):
        super(BaseV1ImageTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseV1ImageTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV1ImageTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV1ImageTest, cls).resource_setup()


class BaseV1ImageMembersTest(base_tempest_image.BaseV1ImageMembersTest):
    @classmethod
    def skip_checks(cls):
        super(BaseV1ImageMembersTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseV1ImageMembersTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV1ImageMembersTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV1ImageMembersTest, cls).resource_setup()


class BaseV2ImageTest(base_tempest_image.BaseV2ImageTest):
    @classmethod
    def skip_checks(cls):
        super(BaseV1ImageMembersTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseV2ImageTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV2ImageTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV2ImageTest, cls).resource_setup()


class BaseV2MemberImageTest(base_tempest_image.BaseV2MemberImageTest):
    @classmethod
    def skip_checks(cls):
        super(BaseV2MemberImageTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseV2MemberImageTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV2MemberImageTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV2MemberImageTest, cls).resource_setup()


class BaseV1ImageAdminTest(base_tempest_image.BaseV1ImageAdminTest):
    @classmethod
    def skip_checks(cls):
        super(BaseV1ImageAdminTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseV1ImageAdminTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV1ImageAdminTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV1ImageAdminTest, cls).resource_setup()


class BaseV2ImageAdminTest(base_tempest_image.BaseV2ImageAdminTest):
    @classmethod
    def skip_checks(cls):
        super(BaseV2ImageAdminTest, cls).skip_checks()

    @classmethod
    def setup_credentials(cls):
        super(BaseV2ImageAdminTest, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(BaseV2ImageAdminTest, cls).setup_clients()

    @classmethod
    def resource_setup(cls):
        super(BaseV2ImageAdminTest, cls).resource_setup()
