from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Bobbys posts',
            description='Посты Бобби',
            slug='bobbys'
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Bobby')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Привет',
            author=self.user,
            group=self.group
        )
        self.user2 = User.objects.create_user(username='Sara')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_url_exists_at_desired_location(self):
        url_names = ('/',
                     f'/group/{self.group.slug}/',
                     f'/{self.user}/',
                     f'/{self.user}/{self.post.id}/')
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_url_exists_user_at_desired_location(self):
        url_names = ('/new/',
                     f'/{self.user}/{self.post.id}/edit/')
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_username_post_id_edit_url_guest_exists_at_desired_location(self):
        response = self.guest_client.get(f'/{self.user}/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_user_post_id_edit_url_authorized_exists_at_desired_location(self):
        response = self.authorized_client2.get(
            f'/{self.user}/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'index.html': '/',
            'new.html': '/new/',
            'group.html': f'/group/{self.group.slug}/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template2(self):
        templates_url_names = {
            'new.html': f'/{self.user}/{self.post.id}/edit/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_username_post_id_edit_url_authorized_redirect(self):
        response = self.authorized_client2.get(
            f'/{self.user}/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, f'/{self.user}/{self.post.id}/')

    def test_username_post_id_edit_url_guest_redirect(self):
        response = self.guest_client.get(
            f'/{self.user}/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/{self.user}/{self.post.id}/edit/')

    def test_wrong_url_returns_404(self):
        response = self.guest_client.get('/oops/i/did_it/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)
