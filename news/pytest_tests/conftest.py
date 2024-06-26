from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def id_news_for_args(news):
    return (news.id,)


@pytest.fixture
def id_comment_for_args(comment):
    return (comment.id,)


@pytest.fixture
def many_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]

    return News.objects.bulk_create(all_news)


@pytest.fixture
def many_comments(news, author):
    for index in range(10):
        now = timezone.now()
        many_comments = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        many_comments.created = now + timedelta(days=index)
        many_comments.save()
    return many_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }
