
import time

from tempest_common_plugin.common import exceptions as lib_exc


def wait_for_swift_container_deletion(client, container_name):
    """Waits for a container to be deleted."""

    start = int(time.time())
    while True:
        try:
            client.list_container_contents(container_name)
            if int(time.time()) - start >= client.build_timeout:
                message = 'Container failed to delete'
                raise lib_exc.TimeoutException(message)
        except lib_exc.NotFound:
            return


def wait_for_swift_object_deletion(client, container_name, object_name):
    """Waits for a object to be deleted."""

    start = int(time.time())
    while True:
        try:
            client.list_object_metadata(container_name, object_name)
            if int(time.time()) - start >= client.build_timeout:
                message = 'Object failed to delete'
                raise lib_exc.TimeoutException(message)
        except lib_exc.NotFound:
            return


def wait_for_task_image_status(client, task_id, status="success"):
    start = int(time.time())
    while True:
        try:
            body = client.show_tasks(task_id)
            if int(time.time()) - start >= client.build_timeout:
                message = 'Unable to create an image task due timeout'
                raise lib_exc.TimeoutException(message)
            # if we ask for failure status
            if status == "failure" and body['status'] == status:
                break
            elif body['status'] == "failure" and status != "failure":
                message = "unable to create an image task"
                raise lib_exc.TaskCreateException(message)
            elif body['status'] == status:
                break

        except lib_exc.NotFound:
            return
