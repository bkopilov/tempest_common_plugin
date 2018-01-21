import tempest.lib.exceptions as exectpions


class ServiceRestartException(exectpions.TempestException):
    message = "Service restart failed to reach to active status"


class TaskCreateException(exectpions.TempestException):
    message = "Task create failed to reach to success status"
