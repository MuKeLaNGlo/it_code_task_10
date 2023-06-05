from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

import pytest
from news.forms import CommentForm
from news.models import Comment, News

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    """
    Возвращает клиент для выполнения запросов.
    """
    return Client()


@pytest.fixture
def create_news():
    """
    Создает новость.
    """
    def _create_news(title, text):
        return News.objects.create(title=title, text=text)

    return _create_news


@pytest.fixture
def create_comment():
    """
    Создает комментарий.
    """
    def _create_comment(news, author, text):
        return Comment.objects.create(news=news, author=author, text=text)

    return _create_comment


@pytest.fixture
def create_user():
    """
    Создает пользователя.
    """
    def _create_user(username, password):
        return User.objects.create_user(username=username, password=password)

    return _create_user


def test_home_page_has_maximum_10_news(client, create_news):
    """
    Проверяет, что количество новостей на главной странице не превышает 10.
    """
    for i in range(15):
        create_news(f'Test News {i}', f'Test news text {i}')

    url = reverse('news:home')
    response = client.get(url)

    assert len(response.context['news_list']) <= 10


def test_news_sorted_by_date_descending(client, create_news):
    """
    Проверяет, что новости на главной странице
    отсортированы от самой свежей к самой старой.
    """
    create_news('News 1', 'Test news text 1')
    create_news('News 2', 'Test news text 2')
    create_news('News 3', 'Test news text 3')

    url = reverse('news:home')
    response = client.get(url)

    news_list = list(response.context['news_list'])
    assert len(news_list) >= 2
    news_from_db = list(News.objects.order_by('-date')[:10])
    assert news_list == news_from_db


def test_comments_sorted_by_date_ascending(
        client, create_news, create_comment, create_user):
    """
    Проверяет, что комментарии на странице отдельной
    новости отсортированы в хронологическом порядке.
    """
    news = create_news('Test News', 'Test news text')
    user1 = create_user('user1', 'password')
    user2 = create_user('user2', 'password')
    user3 = create_user('user3', 'password')

    create_comment(news, author=user1, text='Comment 1')
    create_comment(news, author=user2, text='Comment 2')
    create_comment(news, author=user3, text='Comment 3')

    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)

    comments = list(response.context[0]['news'].comment_set.all())
    assert len(comments) >= 2
    comments_from_db = list(
        Comment.objects.filter(news=news).order_by('created')
    )
    assert comments == comments_from_db


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
