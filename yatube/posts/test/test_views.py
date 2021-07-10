import shutil
import tempfile

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='Bobby')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Bobbys posts',
            description='Посты Бобби',
            slug='bobbys'
        )
        cls.post = Post.objects.create(
            text='Привет',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.user2 = User.objects.create_user(username='Sara')
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)
        cls.user3 = User.objects.create_user(username='Kevin')
        cls.authorized_client3 = Client()
        cls.authorized_client3.force_login(cls.user3)
        cls.guest_client = Client()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()

    def test_main_uses_correct_template(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    def test_new_page_uses_correct_template(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertTemplateUsed(response, 'new.html')

    def test_group_use_correct_template(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertTemplateUsed(response, 'group.html')

    def test_main_shows_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_pages_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(response.context['group'].description,
                         self.group.description)
        self.assertEqual(response.context['group'].slug, self.group.slug)
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_new_shows_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': f'{self.user}',
                    'post_id': f'{self.post.id}'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'profile', kwargs={'username': f'{self.user}'}))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_userd_post_id_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': self.user,
                    'post_id': self.post.id}))
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_shows_on_main(self):
        response = self.authorized_client.get(reverse('index'))
        first_post = response.context['page'][0]
        post_text = first_post.text
        self.assertEqual(post_text, self.post.text)

    def test_post_shows_on_group(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        first_post = response.context['page'][0]
        group = first_post.group.title
        self.assertEqual(group, self.group.title)

    def test_cache_index_works(self):
        cache.clear()
        new_post = Post.objects.create(
            text='Проверка кэша',
            author=self.user,
            group=self.group)
        response = self.client.get(reverse('index'))
        new_post.delete()
        self.assertEqual(response.context.get('page').object_list[0].text,
                         new_post.text)
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertNotEqual(response.context.get('page').object_list[0].text,
                            new_post.text)

    def test_user_follow_unfollow_author(self):
        self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': self.user2})
        )
        self.assertEqual(self.user.follower.count(), 1)
        self.authorized_client.get(
            reverse('profile_unfollow', kwargs={'username': self.user2})
        )
        self.assertEqual(self.user.follower.count(), 0)

    def test_new_post_in_feed_of_follow_user(self):
        self.authorized_client2.get(
            reverse('profile_follow', kwargs={'username': self.user}))
        response = self.authorized_client2.get(reverse('follow_index'))
        first_post = response.context['page'][0]
        self.assertEqual(first_post.text, self.post.text)
        response = self.authorized_client3.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 0)

    def test_only_auth_user_comment(self):
        response = self.authorized_client2.get(reverse('add_comment', 
                                                       kwargs={'username': self.user,
                                                               'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        response = self.guest_client.get(reverse('add_comment', 
                                                       kwargs={'username': self.user,
                                                               'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)







class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Bobby')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Bobbys posts',
            description='Посты Бобби',
            slug='bobbys'
        )
        for item in range(15):
            cls.post = Post.objects.create(
                text=f'Пост №{item}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        cache.clear()

    def test_first_page_index_contains_ten_records(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page')), 10)

    def test_second_page_index_contains_five_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page')), 5)

    def test_first_page_profile_contains_ten_records(self):
        response = self.client.get(reverse(
            'profile', kwargs={'username': f'{self.user}'}))
        self.assertEqual(len(response.context.get('page')), 10)

    def test_second_page_profile_contains_five_records(self):
        response = self.client.get(reverse(
            'profile', kwargs={'username': f'{self.user}'}) + '?page=2')
        self.assertEqual(len(response.context.get('page')), 5)

    def test_first_page_group_contains_ten_records(self):
        response = self.client.get(reverse(
            'group_posts', kwargs={'slug': f'{self.group.slug}'}))
        self.assertEqual(len(response.context.get('page')), 10)

    def test_second_page_group_contains_five_records(self):
        response = self.client.get(reverse(
            'group_posts', kwargs={'slug': f'{self.group.slug}'}) + '?page=2')
        self.assertEqual(len(response.context.get('page')), 5)
