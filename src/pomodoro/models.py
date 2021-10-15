import uuid
import datetime
from django.db import models
from .enums import TaskStatus


class Task(models.Model):
    id = models.UUIDField(
        primary_key=True,
        help_text="ID of the Task",
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        default="", max_length=64, help_text="Name of the Task"
    )
    duration = models.IntegerField(
        default=25 * 60, help_text="Duration of the Task in seconds.")
    remainder = models.IntegerField(
        default=25 * 60, help_text="time remaining of the Task in seconds.")
    status = models.IntegerField(
        choices=TaskStatus.choices,
        default=TaskStatus.CREATED,
        help_text="Status of Task"
    )
    webhook_url = models.URLField(
        blank=True, help_text="Webhook of the Task.")
    start_at = models.DateTimeField(
        null=True, blank=True, help_text="Starting date time of the Task."
    )
    end_at = models.DateTimeField(
        null=True, blank=True, help_text="Starting date time of the Task."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Creation date time of the Task.")

    async_task_id = models.UUIDField(
        null=True, help_text="Id of celery async task.")

    @property
    def duration_timedelta(self):
        return datetime.timedelta(seconds=self.duration)

    @property
    def remainder_timedelta(self):
        return datetime.timedelta(seconds=self.remainder)
