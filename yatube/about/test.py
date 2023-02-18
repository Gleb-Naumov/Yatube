from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page(self):
        responce = self.guest_client.get('/about/author/')
        self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_tech_page(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
