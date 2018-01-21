

from tempest import config
from tempest import test

from tempest_common_plugin.tests.api.object_storage\
    import base

CONF = config.CONF


class ContainerList(base.BaseObjectTest):

    @classmethod
    def resource_setup(cls):
        super(ContainerList, cls).resource_setup()

    @test.idempotent_id('bbe24203-5469-4819-adef-6ccd95efb759')
    def test_list_reverese_container(self):
        container_names = ["a", "b", "c"]
        for container_name in container_names:
            resp, _ = self.container_client.create_container(container_name)
            self.containers.append(container_name)
            self.assertHeaders(resp, 'Container', 'PUT')
        _, body = self.container_client.list_container_contents(
            "", {'reverse': 'on'})
        self.assertEqual(container_names[::-1], body)
