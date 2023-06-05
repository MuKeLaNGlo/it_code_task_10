from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='user', password='password'
        )
        cls.superuser = User.objects.create_user(
            username='superuser', password='superpassword'
        )
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.user
        )

    def test_home_page_accessible_to_anonymous_user(self):
        """
        Проверка, страница доступна анонимному пользователю
        """
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_has_access_to_note_pages(self):
        """
        Проверка, что аутентифицированному пользователю доступна
        страница со списком заметок notes/,  страница успешного
        добавления заметки done/, страница добавления новой заметки add/.
        """
        self.client.login(username='user', password='password')
        urls = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_accessible_only_to_note_author(self):
        """
        Проверяем доступ автора к заметкам
        """
        self.client.login(username='superuser', password='superpassword')

        urls = [
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_redirected_to_login_for_note_pages(self):
        """
        Проверяем редирект анонимного пользователя,
        когда он пытается получить доступ к заметкам
        """
        urls = [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(
                response, reverse('users:login') + '?next=' + url
            )

    def test_registration_login_logout_pages_accessible_to_all_users(self):
        """
        Проверяем доступность страниц регистрации, логина, выхода
        для всех пользователей
        """
        urls = [
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:logout'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
