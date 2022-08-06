from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Group, Post, User
from .forms import PostForm


def paginator_posts(request, queryset):
    """Описывает работу пагинатора постов."""
    paginator = Paginator(queryset, settings.CONST_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    """Описывает работу главной страницы."""
    post_list = Post.objects.select_related('author').all()
    context = {'page_obj': paginator_posts(request, post_list)}
    return render(request,'posts/index.html', context)


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
    post_list = author.posts.select_related('author').all()
    context = {
        'author': author,
        'page_obj': paginator_posts(request, post_list)
    }
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
    form = PostForm(request.POST or None)
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
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('group:post_detail', post_id=post.id)

    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    )
