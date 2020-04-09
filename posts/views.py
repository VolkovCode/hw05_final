from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
import random

#@cache_page(60*15)
def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'posts/index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug): 
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator}) 


def new_post(request):
    user = request.user
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not request.user.is_authenticated:
        return redirect(index)
    if request.method == 'POST':
        if form.is_valid():
            n_post = form.save(commit=False)
            n_post.author = user
            n_post.save()
            return redirect('index')
        return render(request, 'posts/new_post.html', {'form': form})        
    form = PostForm()
    return render(request, 'posts/new_post.html', {'form': form})   
    

def profile(request, username):   
    author = get_object_or_404(User, username = username)
    post_list = Post.objects.filter(author = author).order_by('-pub_date')
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    first_post = Post.objects.filter(author = author).order_by('-pub_date')[:1]
    followers = Follow.objects.filter()
    count_followers = Follow.objects.filter(author=author).count()
    count_followering = Follow.objects.filter(user=author).count()   
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=author, user=request.user)     
    else:
        following = []

    count = post_list.count
    return render(request, "posts/profile.html", {'count':count, 'author':author, 'page': page, 
                  'paginator': paginator, 'count_followers': count_followers, 
                  "following": following, 'count_followering': count_followering, 'first_post': first_post})

   
  
def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=profile.pk, id=post_id)
    count = Post.objects.filter(author = profile).count
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id)
    count_followers = Follow.objects.filter(author=profile).count()
    count_followering = Follow.objects.filter(user=profile).count()
    return render(request, "posts/post.html", {"profile":profile, 'post':post, "count":count, 'form': form, 'comments' : comments, "count_followers": count_followers, "count_followering": count_followering})


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id = post_id)
    if request.user != post.author:
        return redirect("post", username, post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        post.text = form.cleaned_data['text']
        post.group = form.cleaned_data['group']
        post.save()
        return redirect("post", username, post_id)
    form = PostForm()
    return render(request, "posts/post_edit.html", {"form": form, 'post':post})    


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post).all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post', username=post.author.username, post_id=post_id,)
        return render(request, "posts/post.html", {'form': form, 'post':post})    
    form = CommentForm()
    return render(request, "posts/comment.html", {"post": post, "form": form, 'comments': comments})
    #return redirect('post', username=post.author.username, post_id=post_id,)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):   
    authors = Follow.objects.filter(user=request.user).values_list('author', flat=True)
    post_list = Post.objects.filter(author__in=authors).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'posts/follow.html', {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username = username)
    user = request.user   
    if author not in list(Follow.objects.filter(user=request.user).values_list('author', flat=True)):
        if user != author:
            Follow.objects.create(user=user, author=author)   
            return redirect("profile", username=username)
        else:
            return redirect("profile", username=username)        
    

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username = username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect("profile", username=username)  
