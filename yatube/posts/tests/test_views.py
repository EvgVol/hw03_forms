from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group,Post
from yatube.settings import CONST_TEN

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title = 'Тестовая группа',
            slug = 'test_slug',
            description = 'Описание тестовой группы',
        )
        cls.user = User.objects.create_user(username='Test_user')
        cls.post = Post.objects.create(
            author = cls.user,
            text = 'Тестовый текст',
            group = cls.group
        )
        cls.templat = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': cls.group.slug})
            ),
            'posts/profile.html': (reverse('posts:profile', kwargs={'username': cls.post.author})),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': cls.post.id})
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': cls.post.id})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        cls.context_test = {
            reverse('posts:index'): 'Тест-главная страница',
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}): 'Тест-группа',
            reverse('posts:profile', kwargs={'username': cls.post.author}): 'Тест страница автора',
            reverse('posts:post_detail', kwargs={'post_id': cls.post.id}): 'Тест поста',
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}): 'Тест корр поста',
        }
        cls.check_create_post = {
            reverse('posts:index'): 'Тест-главная страница',
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}): 'Тест-группа',
            reverse('posts:profile', kwargs={'username': cls.post.author}): 'Тест страница автора',
        }


    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.unauthorized_client = Client()
    
    def test_pages_uses_correct_template(self):
        """Проверяем используемые шаблоны."""
        for template, reverse_name in self.templat.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_unauth_page_uses(self):
        """Url-шаблон для проверки неавторизованного пользователя ."""
        response = self.unauthorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertTemplateNotUsed(response, 'posts/create_post.html')


    def test_views_page_show_correct_context(self):
        """Шаблон views сформирован с правильным контекстом -
        списком постов."""
        for adress, context_T in self.context_test.items():
            with self.subTest(context_T=context_T):
                error_message = f'Шаблон {context_T} сформирован не верно'
                response = self.authorized_client.get(adress)
                post = response.context['post']
                self.assertEqual(post.author, self.post.author, error_message)
                self.assertEqual(post.text, self.post.text, error_message)
                self.assertEqual(post.group, self.post.group, error_message)


    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом -
        списком постов, отфильтрованных по группе.
        """
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        )
        first_object = response.context['group']
        group_title = first_object.title
        group_slug = first_object.slug
        self.assertEqual(group_title, 'Тестовая группа')
        self.assertEqual(group_slug, 'test_slug')

    def test_check_create_post(self):
        """Проверка шаблонов."""
        post_2 = Post.objects.create(
            author = self.user,
            text = 'Тестовый текст',
            group = self.group,
        )
        for i, j in self.check_create_post.items():
            with self.subTest(j = j):
                error_message = f'Пост {j} не найден на странице'
                response = self.unauthorized_client.get(i)
                post = response.context['page_obj'][0]
                self.assertEqual(post.id, post_2.id, error_message)
        

class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username = "test_username",
        )
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group)
            )
        Post.objects.bulk_create(cls.posts)
    
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        list_urls = {
            reverse("posts:index"): "index",
            reverse("posts:group_list", 
                kwargs={"slug": "test_slug"}): "group_list",
            reverse("posts:profile", 
                kwargs={"username": "test_username"}): "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(
                response.context.get('page_obj').object_list), CONST_TEN)

    def test_second_page_contains_three_posts(self):
        list_urls = {
            reverse("posts:index"): "index",
            reverse("posts:group_list", kwargs={"slug": "test_slug"}):
            "group",
            reverse("posts:profile", kwargs={"username": "test_username"}):
            "profile",
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url + "?page=2")
            self.assertEqual(len(response.context.get('page_obj').object_list), 3)
