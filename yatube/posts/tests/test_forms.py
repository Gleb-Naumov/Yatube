import shutil
import tempfile
from posts.models import Post, Group, User, Comment
from posts.forms import PostForm
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='gleb')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.comment = Comment.objects.create(
            text='Тестовый коммент',
            author=cls.user,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorizade_user = Client()
        self.authorizade_user.force_login(self.user)

    def test_create_new_post(self):
        post_count = Post.objects.count()
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
        post_form = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorizade_user.post(reverse('posts:post_create'),
                                              data=post_form, follow=True)
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': 'gleb'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(self.group.id, post_form['group'])
        self.assertEqual(self.post.text, post_form['text'])
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст',
            group=self.group,
            image='posts/small.gif'
        ).exists())

    def test_edit_post(self):
        post_count = Post.objects.count()
        post_form = {
            'text': 'изменения текста',
            'group': self.group.id,
        }
        response = self.authorizade_user.post(reverse('posts:post_edit',
                                              kwargs={'post_id': '1'}),
                                              data=post_form, follow=True)
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': '1'}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(self.group.id, post_form['group'])
        self.assertEqual(post_form['text'], 'изменения текста')

    def test_comments_form(self):
        comment_count = Comment.objects.count()
        comment_form = {
            'text': 'Тестовый текст',
        }
        response = self.authorizade_user.post(reverse('posts:add_comment',
                                              kwargs={'post_id': '1'}),
                                              data=comment_form, follow=True)
        self.assertEqual(comment_form['text'], 'Тестовый текст')
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': '1'}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
