import requests
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from . import tasks as l_tasks


# Create your tests here.
class TestTask(TestCase):

    def test_update_rule_test(self):
        l_tasks.update_rule()

    def test_update_rule_to_prometheus_and_reload(self):
        l_tasks.update_rule_to_prometheus_and_reload()

    # def test_tttt(self):
    #     raise Exception("eee_ttt")
    #
    # def test_tttt2(self):
    #     raise Exception("eee_ttt2")


class MetricGroupTests(APITestCase):

    def test_create(self):
        url = reverse("metric-groups")
        data = {
            "name": "SSV Account",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

