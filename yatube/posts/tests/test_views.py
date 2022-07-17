from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.test import TestCase, Client, override_settings
from ..models import Post, Group, User
from django.urls import reverse
from django import forms
import shutil
import tempfile
from django.conf import settings


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="slug555",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            id="30",
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=False)

    def setUp(self):
        self.guest_client = Client()
        self.user = PostsPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_list", kwargs={"slug": PostsPagesTests.group.slug}
            ),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": PostsPagesTests.user}
            ),
            "posts/post_detail.html": (
                reverse(
                    "posts:post_detail",
                    kwargs={"post_id": PostsPagesTests.post.id},
                )
            ),
            "posts/create_post.html": reverse(
                "posts:post_edit", kwargs={"post_id": PostsPagesTests.post.id}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        template = "posts/create_post.html"
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        page_object = response.context.get("page_obj")[0]
        self.assertIsInstance(page_object, Post)

    def test_group_page_show_correct_context(self):
        """в group_list передан объект класса Post и группа"""
        response = self.authorized_client.get(
            reverse(
                "posts:group_list", kwargs={"slug": PostsPagesTests.group.slug}
            )
        )
        page_object = response.context.get("page_obj")[0]
        group = response.context.get("group")
        self.assertIsInstance(page_object, Post)
        self.assertEqual(group, PostsPagesTests.group)

    def test_many_pages_show_correct_context(self):
        """в profile передан объект класса Post и автор"""
        templates_pages_names = {
            reverse("posts:index"),
            reverse(
                "posts:group_list", kwargs={"slug": PostsPagesTests.group.slug}
            ),
            reverse(
                "posts:profile", kwargs={"username": PostsPagesTests.user}
            ),
        }

        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post_obj = response.context["page_obj"][0]
                post_text = post_obj.text
                self.assertEqual(post_text, PostsPagesTests.post.text)
                post_author = post_obj.author
                self.assertEqual(post_author, PostsPagesTests.post.author)
                post_group = post_obj.group
                self.assertEqual(post_group, PostsPagesTests.post.group)

    def test_post_detail_page_show_correct_context(self):
        reverse_name = reverse(
            "posts:post_detail",
            kwargs={"post_id": PostsPagesTests.post.id},
        )
        response = self.authorized_client.get(reverse_name)
        post_obj = response.context["post"]
        post_text = post_obj.text
        self.assertEqual(post_text, PostsPagesTests.post.text)
        post_author = post_obj.author
        self.assertEqual(post_author, PostsPagesTests.post.author)
        post_group = post_obj.group
        self.assertEqual(post_group, PostsPagesTests.post.group)

    def test_create_pages_show_correct_context(self):
        """в profile передан объект класса Post и автор"""
        templates_pages_names = {
            reverse(
                "posts:post_edit", kwargs={"post_id": PostsPagesTests.post.id}
            ),
            reverse("posts:post_create"),
        }

        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                text_field = response.context["form"].fields.get("text")
                group_field = response.context["form"].fields.get("group")
                char_field = forms.fields.CharField
                choise_field = forms.ModelChoiceField
                self.assertIsInstance(text_field, char_field)
                self.assertIsInstance(group_field, choise_field)

    def test_pages_show_correct_image_context(self):
        """profile передан объект класса image"""
        templates_pages_names = {
            reverse("posts:index"),
            reverse(
                "posts:group_list", kwargs={"slug": PostsPagesTests.group.slug}
            ),
            reverse(
                "posts:profile", kwargs={"username": PostsPagesTests.user}
            ),
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                image_field = response.context["page_obj"][0].image.name
                image_name = "posts/small.gif"
                self.assertEqual(image_field, image_name)

        reverse_name = reverse(
            "posts:post_detail",
            kwargs={"post_id": PostsPagesTests.post.id},
        )
        response = self.authorized_client.get(reverse_name)
        image_field = response.context["post"].image.name
        image_name = "posts/small.gif"
        self.assertEqual(image_field, image_name)
