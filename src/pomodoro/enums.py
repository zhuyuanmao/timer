from django.db.models import TextChoices, IntegerChoices
from django.utils.translation import gettext_lazy as _


class TaskStatus(IntegerChoices):
    CANCELED = 0
    CREATED = 2
    STARTED = 3
    COMPLETED = 4
    PAUSED = 5
