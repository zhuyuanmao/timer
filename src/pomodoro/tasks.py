from celery import shared_task
from .models import Task


@shared_task
def change_task_status(pk, status):
    """
    Change Task object status

    params: 
        pk: primary key of Task object.
        status: enumerate type of Task Status

    return:
        None.
    """
    task = Task.objects.get(id=pk)
    task.status = status
    task.remainder = 0
    task.save()

    # TODO: Send a request to the webhook.
