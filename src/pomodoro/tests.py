import celery
from rest_framework import status
import uuid
from .models import Task
from rest_framework.test import APITestCase
from unittest.mock import MagicMock, PropertyMock
from unittest.mock import patch
from pomodoro.views import change_task_status
from celery.result import AsyncResult


class TaskTests(APITestCase):
    task = None

    def setUp(self) -> None:
        data = {
            "name": "test",
            "duration": 2000,
            "webhook_url": "http://example.webhook.com"
        }
        self.task = Task.objects.create(**data)

    def test_create_task(self):
        url = "/tasks"
        data = {
            "name": "study",
            "duration": 2000,
            "webhook_url": "http://example.webhook.com"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Task.objects.all().order_by(
            "-created_at").first().name, 'study')

    def test_retrieve_tasks(self):
        url = "/tasks"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_task_with_id(self):
        url = "/tasks" + "/" + str(self.task.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.task.id))

    @patch('pomodoro.views.change_task_status.apply_async')
    def test_to_start_a_task(self, mock_apply_async):
        url = "/tasks" + "/" + str(self.task.id) + "/operations"
        mock_apply_async.return_value = AsyncResult(str(self.task.id))
        data = {
            "operation": "start"
        }
        response = self.client.post(url, data=data, format='json')
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.task.status, 3)
        self.assertNotEqual(self.task.start_at, None)
        self.assertNotEqual(self.task.end_at, None)

    @patch('pomodoro.views.change_task_status.apply_async')
    def test_to_start_an_invalid_state_task(self, mock_apply_async):
        url = "/tasks" + "/" + str(self.task.id) + "/operations"
        mock_apply_async.return_value = AsyncResult(str(self.task.id))
        data = {
            "operation": "pause"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "operation": "resume"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('pomodoro.views.change_task_status.apply_async')
    def test_to_pause_an_state_task(self, mock_apply_async):
        url = "/tasks" + "/" + str(self.task.id) + "/operations"
        data = {
            "operation": "start"
        }
        self.task.refresh_from_db()
        mock_apply_async.return_value = AsyncResult(str(self.task.id))
        self.client.post(url, data=data, format='json')
        data = {
            "operation": "pause"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED)

    @patch('pomodoro.views.change_task_status.apply_async')
    def test_to_pause_an_invalid_state_task(self, mock_apply_async):
        url = "/tasks" + "/" + str(self.task.id) + "/operations"
        data = {
            "operation": "start"
        }
        self.task.refresh_from_db()
        mock_apply_async.return_value = AsyncResult(str(self.task.id))
        self.client.post(url, data=data, format='json')
        data = {
            "operation": "pause"
        }
        self.client.post(url, data=data, format='json')
        data = {
            "operation": "start"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.post(url, data=data, format='json')
        data = {
            "operation": "pause"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('pomodoro.views.change_task_status.apply_async')
    def test_to_resume_a_task(self, mock_apply_async):
        url = "/tasks" + "/" + str(self.task.id) + "/operations"
        data = {
            "operation": "start"
        }
        self.task.refresh_from_db()
        mock_apply_async.return_value = AsyncResult(str(self.task.id))
        self.client.post(url, data=data, format='json')
        data = {
            "operation": "pause"
        }
        self.client.post(url, data=data, format='json')
        data = {
            "operation": "resume"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('pomodoro.views.change_task_status.apply_async')
    def test_to_resume_an_invalid_state_task(self, mock_apply_async):
        url = "/tasks" + "/" + str(self.task.id) + "/operations"
        data = {
            "operation": "start"
        }
        self.task.refresh_from_db()
        mock_apply_async.return_value = AsyncResult(str(self.task.id))
        self.client.post(url, data=data, format='json')
        data = {
            "operation": "pause"
        }
        self.client.post(url, data=data, format='json')
        data = {
            "operation": "pause"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "operation": "start"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
