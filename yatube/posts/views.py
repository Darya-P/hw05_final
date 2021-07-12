from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    user = request.user
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = user.is_authenticated and (
        Follow.objects.filter(user=user, author=author).exists())
    return render(request, 'profile.html', {'author': author, 'page': page,
                                            'following': following})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    author = get_object_or_404(User, username=username)
    user = request.user
    form = CommentForm()
    comments = post.comments.all()
    following = user.is_authenticated and (
        Follow.objects.filter(user=user, author=author).exists())
    return render(request, 'post.html', {'post': post, 'author': author,
                                         'form': form, 'comments': comments,
                                         'following': following})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'is_edit': False})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'new.html', {'form': form, 'post': post,
                  'is_edit': True})


def page_not_found(request, exception=None):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, post_id, username):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', post_id=post.id, username=post.author.username)
    comments = post.comments.all()
    context = {'form': form,
               'comments': comments,
               'post': post}
    return render(request, 'comments.html', context)


@login_required
def follow_index(request):
    user = request.user
    post_list = Post.objects.filter(author__following__user=user)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=user)
    else:
        return redirect('index')
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        unfollow = Follow.objects.filter(author=author, user=request.user)
        unfollow.delete() 
        return redirect('profile', author.username)
    else:
        return redirect('index')
