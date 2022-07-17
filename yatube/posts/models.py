from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint


User = get_user_model()


class Group(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField("community name", max_length=200)
    slug = models.SlugField("community id", unique=True)
    description = models.TextField("community description")


class Post(models.Model):
    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text

    text = models.TextField("the text of the post")
    pub_date = models.DateTimeField("date of publication", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="author",
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="community",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="author",
    )
    text = models.TextField("the text of the comment")
    created = models.DateTimeField("date of comment", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )
    UniqueConstraint(fields=["user", "author"], name="unique_follow")
