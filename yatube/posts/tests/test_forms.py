from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post,Group
from ..forms import PostForm

User = get_user_model()


class PostCreateForm(TestCase):
    """Проверка формы со странице создания поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title = 'Заголовок тестовой группы',
            slug = 'test_slug',
            description = 'Тестовое описание'
        )
        cls.user = User.objects.create_user(username = 'test_name')
        cls.post = Post.objects.create(
            text = 'Тестовый текст',
            group = cls.group,
            author = cls.user
        )
        cls.form = PostForm()
    
    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_check_send_form_post(self):
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Тестовые данные',
            'group': self.group.id
        }
        response_guest = self.guest_client.post(
            reverse('posts:post_create'),
            data = form_data,
            follow = False
        )
        self.assertEqual(response_guest.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), 1)
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data = form_data,
            follow = True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(Post.objects.filter(
            text = form_data['text'],
            group = form_data['group']
            ).exists()
        )

    def test_edit_post(self):
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.id,
        }
        response_guest = self.guest_client.post(
            reverse('posts:post_edit', 
                kwargs={
                        'post_id': self.post.id
                    }),
            data = form_data,
            follow = False
        )
        self.assertEqual(response_guest.status_code, HTTPStatus.FOUND)
        response = self.auth_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.post.id
                    }),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.group.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.text, form_data['text'])


        
        