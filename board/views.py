from django.shortcuts import render, get_object_or_404, redirect
from .models import Board, Thread, Post
from .forms import PostForm, PostReply
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .api import UwUnify

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
            post.name = request.user.username
            post.thread = thread
            post.created_at = timezone.now()
            post.message = UwUnify(post.message)
            post.save()
            return redirect('thread_view', board_code=board_code, thread_id=thread_id)
    else:
        form = PostReply()

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
            post.name = request.user.username
            post.message = UwUnify(post.message)
            post.save()

            return redirect('thread_view', board_code=board_code, thread_id=thread.id)
    else:
        form = PostForm()

    return render(request, 'board/create_thread.html', {
        'board': board,
        'form': form
    })

@login_required
def delete_post(request, board_code, thread_id, post_id):
    board = get_object_or_404(Board, code=board_code)
    thread = get_object_or_404(Thread, id=thread_id, board=board)
    post = get_object_or_404(Post, id=post_id, thread=thread)
    if request.user.username == post.name:
        if post.is_op:
            thread.delete()
            message = "Thread deleted successfully"
            return redirect('board_view', board_code=board_code)
        else:
            post.delete()
            message = "Post deleted successfully"
    return redirect('thread_view', board_code=board_code, thread_id=thread_id)


@login_required
def edit_post(request, board_code, thread_id, post_id):
    board = get_object_or_404(Board, code=board_code)
    thread = get_object_or_404(Thread, id=thread_id, board=board)
    post = get_object_or_404(Post, id=post_id, thread=thread)

    # Permission check - return early if not authorized
    if not (request.user.is_staff or request.user.username == post.name):
        return redirect('thread_view', board_code=board_code, thread_id=thread_id)

    # Determine which for   m to use
    FormClass = PostForm if post.is_op else PostReply

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.edited_at = timezone.now()  # Track edit time
            edited_post.message = UwUnify(edited_post.message)
            edited_post.save()

            return redirect('thread_view', board_code=board_code, thread_id=thread_id)
    else:
        form = FormClass(instance=post)

    context = {
        'board': board,
        'thread': thread,
        'post': post,
        'form': form
    }
    return render(request, 'board/edit_post.html', context)