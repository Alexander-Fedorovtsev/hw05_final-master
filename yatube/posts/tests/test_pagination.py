from django.test import TestCase, Client
from django.test import TestCase, Client
from ..models import Post, Group, User
from django.urls import reverse


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth2")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="slug555",
            description="Тестовое описание",
        )
        for i in range(15):
            Post.objects.create(
                author=cls.user,
                text=f"Тестовый пост {i}",
                id=f"3{i}",
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_three_pages_contains_ten_records(self):
        templates_pages_names = {
            reverse("posts:index"),
            reverse(
                "posts:group_list",
                kwargs={"slug": PaginatorViewsTest.group.slug},
            ),
            reverse(
                "posts:profile", kwargs={"username": PaginatorViewsTest.user}
            ),
        }

        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                obj_len = len(response.context["page_obj"])
                self.assertEqual(obj_len, 10)
