from django.test import Client, TestCase
from posts.models import Group, Post, User
from http import HTTPStatus
from django.core.cache import cache


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Gleb')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='09.02.2023',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_create_post(self):
        """Страница /create/ доступна авторизированому пользователю"""
        response = self.authorized_client.get('/create/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_redirect(self):
        """Страница /create/ перенаправляет не авторизированова пользователя"""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit(self):
        """
        Страница /post/post_id/edit/
        перенаправляет не авторизированова пользователя
        """
        response = self.guest_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_post_edit_author(self):
        """Страница  /posts/1/edit/ видна авторизованому пользователю"""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def unexisting_page(self):
        """Неизвестная страница не найдена"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        template_urls_name = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Gleb/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for template, address in template_urls_name.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, address)

    def test_all_page_for_guest(self):
        all_page = {
            'home_page': '/',
            'group_page': '/group/test-slug/',
            'profile_page': '/profile/Gleb/',
            'post_page': '/posts/1/',
        }
        for name, addres in all_page.items():
            with self.subTest(addres=addres):
                response = self.guest_client.get(addres)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_all_page_for_guest(self):
        redirect_page = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
        }
        for name, page in redirect_page.items():
            with self.subTest(page=page):
                response = self.guest_client.get(name, follow=True)
                self.assertRedirects(response, page, HTTPStatus.FOUND)

    def test_prosto(self):
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)
