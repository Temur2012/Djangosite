from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Post, Category, Tag, Comment, Profile, Newsletter
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    CommentForm, NewsletterForm, PostForm, SearchForm,
)


def home(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    featured = posts.filter(featured=True)[:3]
    latest = posts[:6]
    popular = posts.order_by('-views')[:5]
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:6]

    context = {
        'featured_posts': featured,
        'latest_posts': latest,
        'popular_posts': popular,
        'categories': categories,
        'newsletter_form': NewsletterForm(),
    }
    return render(request, 'blog/home.html', context)


def post_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    form = SearchForm(request.GET or None)
    q = request.GET.get('q', '').strip()
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(body__icontains=q) | Q(excerpt__icontains=q))

    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'search_form': form,
        'query': q,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    post.views += 1
    post.save(update_fields=['views'])

    related = Post.objects.filter(category=post.category, status='published').exclude(id=post.id)[:3]
    comments = post.comments.filter(active=True, parent__isnull=True).select_related('author')

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                c.parent_id = parent_id
            c.save()
            messages.success(request, "Izohingiz qoshildi!")
            return redirect('post_detail', slug=slug)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related_posts': related,
        'comments': comments,
        'comment_form': form,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = category.posts.filter(status='published')
    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
    })


def category_list(request):
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
    return render(request, 'blog/category_list.html', {'categories': categories})


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.filter(status='published')
    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/tag_detail.html', {
        'tag': tag,
        'page_obj': page_obj,
    })


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}!")
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profil yangilandi!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'blog/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'user_posts': user_posts,
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Maqola yaratildi!")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': "Yangi maqola"})


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "Sizda ruxsat yo'q.")
        return redirect('home')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Maqola yangilandi!")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'title': "Maqolani tahrirlash"})


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "Sizda ruxsat yo'q.")
        return redirect('home')
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Maqola o'chirildi.")
        return redirect('home')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
@require_POST
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.total_likes()})


@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Obuna boldingiz! Rahmat.")
    else:
        messages.error(request, "Ushbu email allaqachon obuna bolgan yoki notogri.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def about(request):
    return render(request, 'blog/about.html')


def contact(request):
    return render(request, 'blog/contact.html')
