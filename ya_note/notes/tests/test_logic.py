from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from pytils.translit import slugify


class TestNoteLogic(TestCase):
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
            title='Note 1', text='Text 1', author=self.user1
        )
        self.note2 = Note.objects.create(
            title='Note 2', text='Text 2', author=self.user2
        )

    def test_authenticated_user_can_create_note(self):
        """
        Тест проверяет, что залогиненный пользователь может создать заметку.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:add')
        data = {
            'title': 'New Note',
            'text': 'Some text',
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(
            response, reverse('notes:success'),
            target_status_code=HTTPStatus.OK
        )

        note_exists = Note.objects.filter(
            title='New Note', text='Some text'
        ).exists()
        self.assertTrue(note_exists)

    def test_anonymous_user_cannot_create_note(self):
        """
        Тест проверяет, что анонимный пользователь не может создать заметку.
        """
        url = reverse('notes:add')
        data = {
            'title': 'New Note',
            'text': 'Some text',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'login')

    def test_duplicate_slug_not_allowed(self):
        """
        Тест проверяет, что невозможно создать две заметки с одинаковым slug.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:add')
        data = {
            'title': 'Note 3',
            'text': 'Text 3',
            'slug': 'note-1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response,
            'form',
            'slug',
            ['note-1 - такой slug уже существует, '
             'придумайте уникальное значение!'],
        )

    def test_automatic_slug_generation(self):
        """
        Тест проверяет, что если при создании заметки не заполнен slug,
        то он формируется автоматически
        с помощью функции pytils.translit.slugify.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:add')
        data = {
            'title': 'Note 3',
            'text': 'Text 3',
            'slug': '',
        }
        response = self.client.post(url, data, follow=True)
        note = Note.objects.get(slug=slugify(data['title']))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(note.slug, slugify(data['title']))

    def test_user_can_edit_own_note(self):
        """
        Тест проверяет, что пользователь
        может редактировать свою заметку.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:edit', args=[self.note1.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_cannot_edit_other_user_note(self):
        """
        Тест проверяет, что пользователь не может
        редактировать заметку другого пользователя.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:edit', args=[self.note2.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_can_delete_own_note(self):
        """
        Тест проверяет, что пользователь может удалить свою заметку.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:delete', args=[self.note1.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_cannot_delete_other_user_note(self):
        """
        Тест проверяет, что пользователь не
        может удалить заметку другого пользователя.
        """
        self.client.login(username='user1', password='password1')
        url = reverse('notes:delete', args=[self.note2.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
