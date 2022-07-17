from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "text",
            "group",
            "image",
        )
        labels = {
            "text": "Текстовая часть",
            "group": "Группа",
            "image": "Картинка поста",
        }
        help_texts = {
            "text": "Введите текст поста",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
