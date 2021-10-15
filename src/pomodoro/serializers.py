from rest_framework import serializers
from .models import Task


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["name", "duration", "webhook_url"]


class TaskRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "name", "status", "duration",
                  "remainder", "start_at", "end_at"]


class TaskOperationSerializer(serializers.Serializer):
    operation = serializers.ChoiceField(
        choices=['pause', 'resume', 'start'],
    )
