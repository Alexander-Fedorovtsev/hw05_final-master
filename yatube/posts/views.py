from django.contrib.auth.decorators import login_required
import datetime
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from .models import Follow, Post, Group, User, Comment
from .forms import PostForm, CommentForm


# Количество записей в выводе на страницу
PAGES: int = 10


def index(request):
    template = "posts/index.html"
    posts = Post.objects.all()
    paginator = Paginator(posts, PAGES)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.all()
    paginator = Paginator(posts, PAGES)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "group": group,
    }
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author_id=author.id)
    count = posts.count
    paginator = Paginator(posts, PAGES)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    user = request.user
    following = False
    if (not user.is_anonymous) and Follow.objects.filter(
        user=user, author=author
    ).exists():
        following = True
    context = {
        "count": count,
        "author": author,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = Post.objects.filter(author_id=post.author.id).count
    form = CommentForm()
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        "post": post,
        "count": count,
        "form": form,
        "comments": comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.published_date = datetime.datetime.now()
        post.save()
        return redirect("posts:profile", username=post.author)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("users:login")
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.pk = post_id
        post.author = request.user
        post.save()
        return redirect("posts:post_detail", post_id=post_id)
    context = {
        "form": form,
        "is_edit": True,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment_form = CommentForm(request.POST or None)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("posts:post_detail", post_id=post_id)
    return redirect("posts:index")


@login_required
def follow_index(request):
    followers = request.user.follower.all()
    authors = list()
    for follower in followers:
        authors.append(follower.author)
    posts = Post.objects.filter(author__in=authors)
    paginator = Paginator(posts, PAGES)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "followers": authors,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if (
        (not user.is_anonymous)
        and (not Follow.objects.filter(user=user, author=author).exists())
        and (user != author)
    ):
        new_follow = Follow(user=user, author=author)
        new_follow.save()
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    del_follow = Follow.objects.get(user=user, author=author)
    del_follow.delete()
    return redirect("posts:profile", username=username)
