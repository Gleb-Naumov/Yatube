from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def test_models_have_correct_objects_name(self):
        post = PostModelTest.post
        text = post.text
        self.assertEqual(text, str(post))

    def test_group_name(self):
        group = PostModelTest.group
        group_name = group.title
        self.assertEqual(group_name, str(group))

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verbose = {
            'text': 'Введите текст',
            'author': 'Автор',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
        }

        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_name(self):
        post = PostModelTest.post

        field_help_text = {
            'text': 'Введите текст в поле',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
