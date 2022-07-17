from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="slug555",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user, text="Тестовая пост", id="30"
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostsURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, 200)

    def test_comment_url_exists_at_desired_location(self):
        """Страница /comment/ доступна авторизованному пользователю."""
        post_id = PostsURLTests.post.id
        response = self.authorized_client.get(
            reverse("posts:add_comment", kwargs={"post_id": post_id})
        )
        self.assertEqual(response.status_code, 302)

    def test_group_url_at_desired_location_anonymous(self):
        """Страница /group/slug/ доступна авторизованному
        пользователю."""
        slug = PostsURLTests.group.slug
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": slug})
        )
        self.assertEqual(response.status_code, 200)

    # Проверяем редиректы для неавторизованного пользователя
    def test_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get("/create/")
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /post/post_id/edit перенаправляет анонимного
        пользователя.
        """
        post_id = PostsURLTests.post.id
        response = self.guest_client.get(
            reverse("posts:post_edit", kwargs={"post_id": post_id})
        )
        self.assertEqual(response.status_code, 302)

    def test_post_detail_exists_at_desired_location_anonymous(self):
        """Страница /post/post_id/edit перенаправляет анонимного
        пользователя.
        """
        post_id = PostsURLTests.post.id
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": post_id})
        )
        self.assertEqual(response.status_code, 200)
