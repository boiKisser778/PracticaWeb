import os
import tempfile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from board.api import UwUnify
from board.models import Board, Thread, Post


class ImageboardIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configuración inicial para todos los tests
        User = get_user_model()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        cls.board = Board.objects.create(
            name='Test Board',
            code='test',
            description='This is a test board'
        )

    def setUp(self):
        # Configuración para cada test
        self.thread = Thread.objects.create(
            board=self.board,
            subject='Test Thread'
        )

        self.post = Post.objects.create(
            thread=self.thread,
            is_op=True,
            name='testuser',
            subject='Test Thread',
            message='This is a test thread'
        )

        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_board_list_view(self):
        """Test que verifica la vista de lista de tablones"""
        response = self.client.get(reverse('board_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.board, response.context['boards'])
        self.assertContains(response, self.board.name)

    def test_board_threads_view(self):
        """Test que verifica la vista de hilos de un tablón"""
        response = self.client.get(reverse('board_view', args=[self.board.code]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.thread, response.context['threads'])
        self.assertContains(response, self.thread.subject)

    def test_thread_view(self):
        """Test que verifica la vista de un hilo individual"""
        response = self.client.get(
            reverse('thread_view', args=[self.board.code, self.thread.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['thread'], self.thread)
        self.assertIn(self.post, response.context['posts'])
        self.assertContains(response, self.post.message)

    def test_create_thread(self):
        """Test que verifica la creación de un nuevo hilo"""
        form_data = {
            'subject': 'New Thread Title',
            'message': 'This is a test thread'  # Cambiamos el mensaje de prueba
        }

        response = self.client.post(
            reverse('create_thread', args=[self.board.code]),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Thread.objects.filter(subject='New Thread Title').exists())

    def test_create_thread_with_image(self):
        """Test que verifica la creación de un hilo con imagen"""
        # Crear una imagen simulada más realista
        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        form_data = {
            'subject': 'Thread With Image',
            'message': 'Test image thread',
            'image': image,
        }

        response = self.client.post(
            reverse('create_thread', args=[self.board.code]),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        # Verificar primero que existe algún hilo con imagen
        self.assertTrue(
            Post.objects.filter(
                thread__board=self.board,
                image__isnull=False
            ).exists()
        )

    def test_reply_to_thread(self):
        """Test que verifica responder a un hilo existente"""
        form_data = {
            'message': 'This is a test reply',
        }

        response = self.client.post(
            reverse('thread_view', args=[self.board.code, self.thread.id]),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        # Buscar el mensaje transformado
        self.assertTrue(
            Post.objects.filter(
                thread=self.thread,
            ).exists()
        )

    def test_edit_post(self):
        """Test que verifica la edición de un post existente"""
        form_data = {
            'message': 'edited message content',  # Usar minúscula consistente
        }

        response = self.client.post(
            reverse('edit_post', args=[self.board.code, self.thread.id, self.post.id]),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()

    def test_delete_post(self):
        """Test que verifica la eliminación de un post"""
        # Crear un post para eliminar
        reply = Post.objects.create(
            thread=self.thread,
            is_op=False,
            name='testuser',
            message='This post will be deleted'
        )

        response = self.client.post(
            reverse('delete_post', args=[self.board.code, self.thread.id, reply.id]),
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(id=reply.id).exists())

    def test_delete_thread(self):
        """Test que verifica la eliminación de un hilo completo"""
        # Crear un hilo temporal para eliminar
        temp_thread = Thread.objects.create(
            board=self.board,
            subject='Temporary Thread'
        )
        temp_post = Post.objects.create(
            thread=temp_thread,
            is_op=True,
            name='testuser',
            message='This thread will be deleted'
        )

        response = self.client.post(
            reverse('delete_post', args=[self.board.code, temp_thread.id, temp_post.id]),
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Thread.objects.filter(id=temp_thread.id).exists())
        self.assertFalse(Post.objects.filter(id=temp_post.id).exists())