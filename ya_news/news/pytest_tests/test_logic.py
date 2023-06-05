from http import HTTPStatus

from django.contrib.auth.models import User
from django.urls import reverse

import pytest
from news.forms import BAD_WORDS, CommentForm
from news.models import Comment, News

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_user():
    def _create_user(username, password):
        return User.objects.create_user(username=username, password=password)
    return _create_user


@pytest.fixture
def create_news():
    def _create_news(title, text):
        return News.objects.create(title=title, text=text)
    return _create_news


@pytest.fixture
def create_comment():
    def _create_comment(text, author, news):
        return Comment.objects.create(text=text, author=author, news=news)
    return _create_comment


def test_anonymous_user_cannot_submit_comment(client, create_news):
    """
    Проверяет, что анонимному пользователю
    недоступна форма для отправки комментария.
    """
    news = create_news('Test News', 'Test news text')
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_user_can_submit_comment(client, create_user, create_news):
    """
    Проверяет, что авторизованному пользователю
    доступна форма для отправки комментария.
    """
    create_user(username='user1', password='password')
    client.login(username='user1', password='password')
    news = create_news('Test News', 'Test news text')
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.parametrize('comment_text', BAD_WORDS)
def test_comment_with_bad_words_not_published(
        client, create_user, create_news, comment_text):
    """
    Проверяет, что комментарий с запрещёнными
    словами не будет опубликован.
    """
    create_user(username='user1', password='password')
    client.login(username='user1', password='password')
    news = create_news('Test News', 'Test news text')
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': comment_text}
    response = client.post(url, data=form_data)

    comment_exists = Comment.objects.filter(text=comment_text).exists()

    assert not comment_exists
    assert 'form' in response.context
    form_errors = response.context['form'].errors.get('text')
    assert bool(form_errors) is True


@pytest.mark.parametrize('comment_text', [
    ('This is a comment without bad words'),
    ('Еще один комментарий без запрещенных слов'),
])
def test_comment_without_bad_words_not_published(
        client, create_user, create_news, comment_text):
    """
    Проверяет, что комментарий без запрещённых
    слов будет опубликован.
    """
    create_user(username='user1', password='password')
    client.login(username='user1', password='password')
    news = create_news('Test News', 'Test news text')
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': comment_text}
    client.post(url, data=form_data)

    comment_exists = Comment.objects.filter(text=comment_text).exists()
    assert comment_exists


def test_authorized_user_can_edit_own_comment(
        client, create_user, create_news, create_comment):
    """
    Проверяет, что авторизованному пользователю
    доступно редактирование своего комментария.
    """
    user = create_user(username='user1', password='password')
    client.login(username='user1', password='password')
    news = create_news('Test News', 'Test news text')
    comment = create_comment(text='Test comment', author=user, news=news)
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    form_data = {
        'text': 'Updated comment'
    }
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == 'Updated comment'


def test_authorized_user_cannot_edit_other_comment(
        client, create_user, create_news, create_comment):
    """
    Проверяет, что авторизованному пользователю
    недоступно редактирование чужого комментария.
    """
    create_user(username='user1', password='password')
    user2 = create_user(username='user2', password='password')
    client.login(username='user1', password='password')
    news = create_news('Test News', 'Test news text')
    comment = create_comment(text='Test comment', author=user2, news=news)
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    form_data = {
        'text': 'Updated comment'
    }
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Test comment'


def test_authorized_user_can_delete_own_comment(
        client, create_user, create_news, create_comment):
    """
    Проверяет, что авторизованному пользователю
    доступно удаление своего комментария.
    """
    user = create_user(username='user1', password='password')
    client.login(username='user1', password='password')
    news = create_news('Test News', 'Test news text')
    comment = create_comment(text='Test comment', author=user, news=news)
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_authorized_user_cannot_delete_other_comment(
        client, create_user, create_news, create_comment):
    """
    Проверяет, что авторизованному пользователю
    недоступно удаление чужого комментария.
    """
    create_user(username='user1', password='password')
    user2 = create_user(username='user2', password='password')
    client.login(username='user1', password='password')
    news = create_news('Test News', 'Test news text')
    comment = create_comment(text='Test comment', author=user2, news=news)
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
