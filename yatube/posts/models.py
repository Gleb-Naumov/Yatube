from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Введите текст',
                            help_text='Введите текст в поле')
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.CASCADE,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите группу')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             null=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(verbose_name='Комментарий',
                            help_text='Введите комментарий в поле',
                            null=True)
    created = models.DateTimeField(verbose_name='Дата публикации',
                                   auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE)
