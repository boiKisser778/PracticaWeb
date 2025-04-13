from django.urls import path
from . import views

urlpatterns = [
    path('', views.board_list, name='board_list'),
    path('<str:board_code>/', views.board_view, name='board_view'),
    path('<str:board_code>/new/', views.create_thread, name='create_thread'),
    path('<str:board_code>/<int:thread_id>/', views.thread_view, name='thread_view'),
]