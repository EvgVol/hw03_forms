from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()

class StatusURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            text = 'Тестовый тест',
            author = User.objects.create_user(
                first_name = "Тест-Имя",
                last_name = "Тест-Фамилия",
                username = "test-username",
                email = "Test@E-Mail.com",
                password = "test",
            )
        )
        Group.objects.create(
            title = 'Тестовая группа',
            slug = 'test_slug',
            description = 'Описание тестовой группы',
        )
        

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        

    def test_out_page(self):
        """Проверка доступных страниц."""
        urlpatterns = (
            '/',
            '/author/',
            '/tech/',
            '/group/test_slug/',
            '/profile/test-username/',
        )
        for url in urlpatterns:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    
    def test_create_post(self):
        """Страница /create/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправляет анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/admin/login/?next=/create/')

    def test_posts_detail_url_redirect_anonymous_on_admin_login(self):
        """Страница /posts/<int:post_id>/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get('/posts/<int:post_id>/edit/', follow=True)
        self.assertRedirects(
            response, ('/admin/login/?next=/posts/<int:post_id>/edit/')
        )
    
    def test_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'author.html': '/author/',
            'tech.html': '/tech/',
        }

        for template, address  in templates_url_names.items():
            with self.subTest(address=address ):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        """Тест несуществующей страницы."""
        response = self.guest_client.get('/unexisting/')
        self.assertEqual(response.status_code, 404)
