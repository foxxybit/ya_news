import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.parametrize(
    'parametrized_client, page_has_form',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
@pytest.mark.django_db
def test_pages_contains_form(
    id_news_for_args, parametrized_client, page_has_form
):
    url = reverse('news:detail', args=id_news_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context and isinstance(
        response.context['form'], CommentForm)) is page_has_form


@pytest.mark.django_db
def test_news_count(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [many_news.date for many_news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, id_news_for_args, many_comments):
    url = reverse('news:detail', args=id_news_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [many_comments.created for many_comments in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
