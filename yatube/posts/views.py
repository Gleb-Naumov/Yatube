from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from .utils import get_page
from django.views.decorators.cache import cache_page


@cache_page(20)
def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = get_page(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = get_page(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = (get_object_or_404(User.objects.
              prefetch_related('posts', 'posts__group'),
              username=username))
    post_list = Post.objects.all().filter(author=author).order_by('-pub_date')
    page_obj = get_page(request, post_list)
    if not Follow.objects.filter(author=author).exists():
        following = False
    else:
        following = True
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    form = CommentForm(request.POST or None)
    post = (get_object_or_404(Post.objects.select_related('author', 'group'),
            id=post_id))
    comments = Comment.objects.all().filter(post=post_id)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return render(request, 'posts:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post.id)
    is_edit = True
    context = {
        'is_edit': is_edit,
        'form': form,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = (Post.objects.all().
                 filter(author__following__user=request.user).
                 order_by('-pub_date'))
    page_obj = get_page(request, post_list)
    follower_user = Follow.objects.all()
    context = {
        'follower_user': follower_user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = (get_object_or_404(User.objects.
              prefetch_related('posts', 'posts__group'),
              username=username))
    if request.user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = (get_object_or_404(User.objects.
              prefetch_related('posts', 'posts__group'),
              username=username))
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
