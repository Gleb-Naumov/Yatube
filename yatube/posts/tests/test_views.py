import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesTest(TestCase):
    text_for_test = 'Тестовое текст'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='gleb')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text=cls.text_for_test,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorizade_user = Client()
        self.authorizade_user.force_login(self.user)
        cache.clear()

    def tearDown(self):
        User.objects.all().delete()
        Post.objects.all().delete()
        Group.objects.all().delete()

    def test_page_use_correct_template(self):
        url_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'gleb'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in url_template.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorizade_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_correct_context(self):
        response = self.authorizade_user.get(reverse('posts:index'))
        first_objects = response.context['page_obj'][0]
        post_text_0 = first_objects.text
        author_0 = first_objects.author
        group_0 = first_objects.group
        image_0 = first_objects.image
        self.assertEqual(post_text_0, self.text_for_test)
        self.assertEqual(author_0, self.user)
        self.assertEqual(group_0, self.group)
        self.assertEqual(image_0, self.post.image)

    def test_group_page_correct_context(self):
        response = self.authorizade_user.get(reverse
                                             ('posts:group_list',
                                              kwargs={'slug': 'test-slug'}))
        first_objects = response.context['page_obj'][0]
        second_objects = response.context['group']
        group_0 = first_objects.group.title
        group_1 = second_objects.title
        post_text_0 = first_objects.text
        image_0 = first_objects.image
        self.assertEqual(post_text_0, self.text_for_test)
        self.assertEqual(group_0, group_1)
        self.assertEqual(image_0, self.post.image)

    def test_profile_page_correct_context(self):
        response = self.authorizade_user.get(reverse
                                             ('posts:profile',
                                              kwargs={'username': 'gleb'}))
        first_objects = response.context['page_obj'][0]
        second_objects = response.context['author']
        posts_text_0 = first_objects.text
        post_author = second_objects.username
        image_0 = first_objects.image
        self.assertEqual(posts_text_0, self.text_for_test)
        self.assertEqual(post_author, self.user.username)
        self.assertEqual(image_0, self.post.image)

    def test_post_detail_page_correct_context(self):
        response = self.authorizade_user.get(reverse('posts:post_detail',
                                                     kwargs={'post_id': '1'}))
        first_objects = response.context['post']
        post_text_0 = first_objects.text
        post_id_0 = first_objects.id
        image_0 = first_objects.image
        self.assertEqual(post_text_0, self.text_for_test)
        self.assertEqual(post_id_0, 1)
        self.assertEqual(image_0, self.post.image)

    def test_create_post_correct_context(self):
        response = self.authorizade_user.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_edit_post_correct_context(self):
        response = self.authorizade_user.get(reverse('posts:post_edit',
                                                     kwargs={'post_id': '1'}))
        first_objects = response.context['post']
        post_id = first_objects.id
        self.assertEqual(post_id, self.post.id)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    @classmethod
    def _bulk_create_posts(cls, quantity=0):
        post = (
            Post(
                text=cls.text_for_test,
                author=cls.user,
                group=cls.group,
            ) for i in range(quantity)
        )
        Post.objects.bulk_create(post, batch_size=quantity or 1)

    def test_paginator(self):
        self._bulk_create_posts(10)
        response = self.authorizade_user.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_second_page(self):
        self._bulk_create_posts(2)
        response = self.authorizade_user.get(reverse('posts:index')
                                             + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
