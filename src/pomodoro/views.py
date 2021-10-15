from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import action
from django.utils import timezone

from app.celery import control
from .models import Task
from .tasks import change_task_status
from .enums import TaskStatus
from .serializers import (
    TaskCreateSerializer,
    TaskRetrieveSerializer,
    TaskOperationSerializer
)


class TaskViewSet(viewsets.ViewSet):
    renderer_classes = [JSONRenderer]

    def list(self, request):
        """
        Get a list of tasks.

        params: None.

        return: 
            tasks: array.

        """
        try:
            tasks = Task.objects.all().order_by("-created_at")
            serializer = TaskRetrieveSerializer(instance=tasks, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """
        Create a task.

        params:
            name: string.
            duration: int.
            webhook_url: string.

        return: 
            id: string.
            name: string.
            status: int.
            duration: int.
            remainder: int.
            start_at: string.
            end_at: string.
        """
        try:
            serializer = TaskCreateSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                name = serializer.validated_data["name"]
                duration = serializer.validated_data["duration"]
                webhook_url = serializer.validated_data["webhook_url"]
                task = Task.objects.create(
                    name=name,
                    duration=duration,
                    remainder=duration,
                    webhook_url=webhook_url
                )
                return Response(
                    data=TaskRetrieveSerializer(instance=task).data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Get a task.

        params: None.

        return: 
            id: string.
            name: string.
            status: int.
            duration: int.
            remainder: int.
            start_at: string.
            end_at: string
        """
        try:
            task = Task.objects.get(id=pk)
            serializer = TaskRetrieveSerializer(instance=task)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"], detail=True, url_path="operations")
    def operate(self, request, pk=None):
        """
        Operate a task.

        params:
            operation: string. e.g. (start, pause, resume)

        return: 
            id: string.
            name: string.
            status: int.
            duration: int.
            remainder: int.
            start_at: string.
            end_at: string
        """
        try:
            serializer = TaskOperationSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                operation = serializer.validated_data["operation"]
                task = Task.objects.get(id=pk)
                self._validate_operations(operation, task)
                # pause to count down the timer.
                if operation == "pause":
                    control.revoke(task_id=str(task.async_task_id), terminate=True,
                                   signal='SIGKILL')
                    time_diff = task.end_at - timezone.now()
                    task.status = TaskStatus.PAUSED
                    task.remainder = max(time_diff.total_seconds(), 0)
                    task.save()

                # resume to count down the timer.
                elif (operation == "resume"):
                    # re-calculate the ending time of the task.
                    res = change_task_status.apply_async(
                        args=(pk, TaskStatus.COMPLETED),
                        countdown=task.remainder
                    )
                    task.status = TaskStatus.STARTED
                    task.end_at = timezone.now() + task.remainder_timedelta
                    task.async_task_id = res.id
                    task.save()
                # start to count down the timer.
                else:
                    res = change_task_status.apply_async(
                        args=(pk, TaskStatus.COMPLETED),
                        countdown=task.remainder
                    )
                    now = timezone.now()
                    task.status = TaskStatus.STARTED
                    task.start_at = now
                    task.end_at = now + task.duration_timedelta
                    task.async_task_id = res.id
                    task.save()
                return Response(
                    data=TaskRetrieveSerializer(instance=task).data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def _validate_operations(self, operation, task):
        """
        Validate a task operation.

        params:
            operation: string.
            task: Task object.

        return: None.
        raise: ValidationError 
        """

        if operation == "pause" and not task.status == TaskStatus.STARTED:
            raise serializers.ValidationError(
                detail="cannot not pause a timer not in a started state.")
        if operation == "resume" and not task.status == TaskStatus.PAUSED:
            raise serializers.ValidationError(
                detail="cannot not resume a timer not in a paused state."
            )
        if operation == "start" and not (task.status == TaskStatus.CREATED):
            raise serializers.ValidationError(
                detail="cannot not start a timer not in a created state."
            )
