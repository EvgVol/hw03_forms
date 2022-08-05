from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Group, Post, User
from .forms import PostForm


def index(request):
    """Описывает работу главной страницы."""
    post_list = Post.objects.select_related('author').all()
    paginator = Paginator(post_list, settings.CONST_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    """Описывает работу страницы сообщества."""
    group = get_object_or_404(Group, slug=slug)

    paginator = Paginator(group.posts.all(), 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'posts/group_list.html',
        {'group': group, 'page_obj': page_obj}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    paginator = Paginator(author.posts.all(), settings.CONST_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'author': author, 'page_obj': page_obj,
               'paginator': paginator, }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_author = Post.objects.filter(
        author__exact=post.author).count()

    return render(
        request,
        'posts/post_detail.html',
        {'post': post, 'post_author': post_author}
    )


@login_required
def post_create(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect(
            'group:profile',
            username=request.user.username
        )

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        post = form.save()
        return redirect('group:post_detail', post_id=post.id)

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post': post}
    )
