from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


class TestContent(TestCase):

    def setUp(self):
        """
        Установка начального состояния для тестов.
        Создание пользователей и заметок.
        """
        self.user1 = User.objects.create_user(
            username='user1', password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password2'
        )
        self.note1 = Note.objects.create(
            title='Заметка 1', text='Текст заметки 1', author=self.user1
        )
        self.note2 = Note.objects.create(
            title='Заметка 2', text='Текст заметки 2', author=self.user1
        )
        self.note3 = Note.objects.create(
            title='Заметка 3', text='Текст заметки 3', author=self.user2
        )

    def test_individual_note_passed_to_notes_list(self):
        """
        Тест проверяет, что отдельная заметка передается на страницу
        со списком заметок в списке object_list в словаре context.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [repr(self.note1), repr(self.note2)],
            ordered=False
        )

    def test_notes_list_contains_only_user_notes(self):
        """
        Тест проверяет, что в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [repr(self.note1), repr(self.note2)],
            ordered=False
        )

    def test_note_create_page_contains_form(self):
        """
        Тест проверяет, что на странице создания заметки передается форма.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_edit_page_contains_form(self):
        """
        Тест проверяет, что на странице
        редактирования заметки передается форма.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:edit', kwargs={'slug': self.note1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsInstance(response.context['form'], NoteForm)
