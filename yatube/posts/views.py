from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .models import Group, Post, User
from .forms import PostForm
from .utils import paginator_posts


def index(request):
    """Описывает работу главной страницы."""
    post_list = Post.objects.select_related('author', 'group').all()
    context = {'page_obj': paginator_posts(request, post_list)}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Описывает работу страницы сообщества."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    context = {
        'group': group,
        'page_obj': paginator_posts(request, post_list)
    }
    return render(
        request,
        'posts/group_list.html',
        context
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').all()
    context = {
        'author': author,
        'page_obj': paginator_posts(request, post_list)
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/post_detail.html', {'post': post})


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect(
            'posts:profile',
            username=request.user.username
        )

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)

    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    )
