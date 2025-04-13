from django.shortcuts import render, get_object_or_404, redirect
from .models import Board, Thread, Post
from .forms import PostForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required
def board_list(request):
    boards = Board.objects.all()
    return render(request, 'board/board_list.html', {'boards': boards})

@login_required
def board_view(request, board_code):
    board = get_object_or_404(Board, code=board_code)
    threads = Thread.objects.filter(board=board).order_by('-is_pinned', '-created_at')
    return render(request, 'board/board_view.html', {'board': board, 'threads': threads})

@login_required
def thread_view(request, board_code, thread_id):
    board = get_object_or_404(Board, code=board_code)
    thread = get_object_or_404(Thread, id=thread_id, board=board)
    posts = Post.objects.filter(thread=thread).order_by('created_at')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.created_at = timezone.now()
            post.ip_address = request.META.get('REMOTE_ADDR')
            post.save()
            return redirect('thread_view', board_code=board_code, thread_id=thread_id)
    else:
        form = PostForm()

    return render(request, 'board/thread_view.html', {
        'board': board,
        'thread': thread,
        'posts': posts,
        'form': form
    })

@login_required
def create_thread(request, board_code):
    board = get_object_or_404(Board, code=board_code)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # Create thread
            thread = Thread.objects.create(
                board=board,
                subject=form.cleaned_data['subject'] or 'No subject',
                created_at=timezone.now()
            )

            # Create OP post
            post = form.save(commit=False)
            post.thread = thread
            post.is_op = True
            post.created_at = timezone.now()
            post.ip_address = request.META.get('REMOTE_ADDR')
            post.save()

            return redirect('thread_view', board_code=board_code, thread_id=thread.id)
    else:
        form = PostForm()

    return render(request, 'board/create_thread.html', {
        'board': board,
        'form': form
    })