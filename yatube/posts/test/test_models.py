from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Bobby')
        cls.post = Post.objects.create(
            text='Мой распрекрасный первый чудесный пост',
            pub_date='2019-05-12',
            author=cls.user
        )

    def test_title_label(self):
        post = PostModelTest.post
        title = post.text[:15]
        self.assertEqual(title, 'Мой распрекрасн')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Bobbys posts',
            description='Посты Бобби'
        )

    def test_title_label(self):
        group = GroupModelTest.group
        title = group.title
        self.assertEqual(title, self.group.title)
