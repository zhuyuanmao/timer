from django.db.models import IntegerChoices


class TaskStatus(IntegerChoices):
    CANCELED = 0
    CREATED = 2
    STARTED = 3
    COMPLETED = 4
    PAUSED = 5
