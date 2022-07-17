from django.test import TestCase, Client
from ..models import Post, Group, User
from django.urls import reverse
from django.core.cache import cache


class PostsCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="slug555",
            description="Тестовое описание",
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.user = PostsCacheTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()
        Post.objects.create(
            author=PostsCacheTests.user,
            text="Тестовый пост",
            id="30",
            group=PostsCacheTests.group,
        )

    def test_index_page_cache_test_context(self):
        """Проверка кеширования главной страницы без очистки кеша"""
        response = self.authorized_client.get(reverse("posts:index"))
        response.context.get("page_obj")[0]
        Post.objects.all().delete()
        result = response.context.get("page_obj")[0]
        self.assertIsNotNone(result)

    def test_index_page_cache_clear_test_context(self):
        """Проверка кеширования главной страницы после очистки кеша"""
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse("posts:index"))
        try:
            result = response.context.get("page_obj")[0]
        except IndexError:
            result = None
        self.assertIsNone(result)
