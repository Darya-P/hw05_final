from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model


User = get_user_model()


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        url_names = ('/about/author/',
                     '/about/tech/')
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
