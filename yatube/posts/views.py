from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post
from .utils import pageobj


def index(request):
    '''
    the function displays the last
     {POSTS_ON_PAGE} posts on the site
    '''
    post_list = Post.objects.select_related('author')
    page_obj = pageobj(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''
    the function displays the last
     {POSTS_ON_PAGE} posts on the site
     from selected group
    '''
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pageobj(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    '''
    the function displays the profile of the selected user
    '''
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = pageobj(posts, request)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    '''
    the function displays the selected post
    '''
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''
    the function create new post
    '''
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
    form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    '''
    the function edit your post
    '''
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    if request.method == 'GET':
        if request.user != post.author:
            return redirect('posts:post_detail', post_id=post.id)
        form = PostForm(instance=post)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)
