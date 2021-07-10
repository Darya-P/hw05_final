from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст записи',
                            help_text='Поле для ввода теста записи')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации',
                                    help_text=('Здесь указывается '
                                               'дата публикации записи')
                                    )
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор записи',
                               help_text='Здесь указан автор записи')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              verbose_name='Имя группы',
                              help_text=('Здесь указана группа, '
                                         'к которой относится запись')
                              )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Комментарий')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария')
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации',
                                    help_text=('Здесь указывается '
                                               'дата публикации записи',),
                                    db_index=True
                                    )

class Follow(models.Model):
    user = models.ForeignKey(User, related_name='follower',
                             on_delete=models.CASCADE,
                             help_text='Пользователь, который подписывается')
    author = models.ForeignKey(User, related_name='following',
                               on_delete=models.CASCADE,
                               help_text='Пользователь, на которого подписываются')

    def __str__(self):
        return f'{self.user} подписан на {self.author}'