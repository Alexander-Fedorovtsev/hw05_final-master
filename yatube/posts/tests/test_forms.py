from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Post, Group, User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
import shutil
import tempfile


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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
        cls.user = User.objects.create_user(username="auth2")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="slug555",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            id="33",
            group=cls.group,
            image=uploaded,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=False)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Текст поста2",
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": PostCreateFormTests.user}
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Текст поста2",
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        post_id = PostCreateFormTests.post.id
        form_data = {
            "text": "Текст поста 88",
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": post_id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": post_id}),
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=post_id,
            ).exists()
        )
        self.assertEqual(
            form_data["text"],
            Post.objects.get(
                id=post_id,
            ).text,
        )

    def test_create_post_unauthorized(self):
        """Форма не создает запись в Post для неавторизованного"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Текст поста2",
        }
        response = self.guest_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        url = reverse("users:login") + "?next=/create/"
        self.assertRedirects(response, url)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text="Текст поста2",
            ).exists()
        )

    def test_edit_post_unauthorized(self):
        """Валидная форма не изменяет запись в Post."""
        posts_count = Post.objects.count()
        post_id = PostCreateFormTests.post.id
        old_post_text = Post.objects.get(id=post_id).text
        form_data = {
            "text": "Текст поста 88",
        }
        response = self.guest_client.post(
            reverse("posts:post_edit", kwargs={"post_id": post_id}),
            data=form_data,
            follow=True,
        )
        url = reverse("users:login") + f"?next=/posts/{post_id}/edit/"
        self.assertRedirects(response, url)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=post_id,
            ).exists()
        )
        self.assertEqual(
            old_post_text,
            Post.objects.get(
                id=post_id,
            ).text,
        )
