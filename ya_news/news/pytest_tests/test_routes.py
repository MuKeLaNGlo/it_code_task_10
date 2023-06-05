from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

import pytest
from news.models import Comment, News

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    """Возвращает клиент для выполнения запросов."""
    return Client()


@pytest.fixture
def create_user():
    """Создает пользователя."""

    def _create_user(username, password):
        return User.objects.create_user(username=username, password=password)

    return _create_user


@pytest.fixture
def create_news():
    """Создает новость."""

    def _create_news(title, text):
        return News.objects.create(title=title, text=text)

    return _create_news


@pytest.fixture
def create_comment():
    """Создает комментарий."""

    def _create_comment(news, author, text):
        return Comment.objects.create(news=news, author=author, text=text)

    return _create_comment


def test_anonymous_user_can_access_home_page(client, create_news):
    """
    Проверяет, что анонимный пользователь
    может получить доступ к главной странице.
    """
    create_news("Test News", "Test news text")
    url = reverse("news:home")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_anonymous_user_can_access_news_detail_page(client, create_news):
    """
    Проверяет, что анонимный пользователь
    может получить доступ к странице с постом.
    """
    news = create_news("Test News", "Test news text")
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("url_name", ["news:delete", "news:edit"])
def test_anonymous_user_redirected_to_login(
    client, create_user, create_news, create_comment, url_name
):
    """
    Проверяет, что анонимный пользователь перенаправляется на страницу
    аутентификации при попытке доступа к страницам
    удаления и редактирования комментариев.
    """
    user = create_user("user", "password")
    news = create_news("Test News", "Test news text")
    comment = create_comment(news, user, "Test comment")

    url = reverse(url_name, kwargs={"pk": comment.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse("users:login"))


def test_unauthorized_user_cannot_edit_other_user_comment(
    client, create_user, create_news, create_comment
):
    """
    Проверяет, что неавторизованный пользователь не может редактировать
    комментарий другого пользователя.
    """
    user1 = create_user("user1", "password1")
    user2 = create_user("user2", "password2")
    news = create_news("Test News", "Test news text")
    comment = create_comment(news, user1, "Test comment")

    client.login(username=user2.username, password="password2")
    url = reverse("news:edit", kwargs={"pk": comment.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("url_name", ["news:delete", "news:edit"])
def test_authorized_user_cannot_edit_other_user_comment(
    client, create_user, create_news, create_comment, url_name
):
    """
    Проверяет, что авторизованный пользователь не может редактировать
    комментарий другого пользователя.
    """
    user1 = create_user("user1", "password1")
    user2 = create_user("user2", "password2")
    news = create_news("Test News", "Test news text")
    comment = create_comment(news, user1, "Test comment")

    client.login(username=user2.username, password="password2")
    url = reverse(url_name, kwargs={"pk": comment.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "url_name", ["users:signup", "users:login", "users:logout"]
)
def test_anonymous_user_can_access_auth_pages(client, url_name):
    """
    Проверяет, что анонимный пользователь может
    получить доступ к страницам аутентификации.
    """
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
