from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(
    author_client, author, form_data, id_news_for_args
):
    url = reverse('news:detail', args=id_news_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, form_data, id_news_for_args):
    url = reverse('news:detail', args=id_news_for_args)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_use_bad_words(author_client, id_news_for_args):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=id_news_for_args)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client, id_comment_for_args, id_news_for_args
):
    url = reverse('news:delete', args=id_comment_for_args)
    news_url = reverse('news:detail', args=id_news_for_args)
    url_to_comments = news_url + '#comments'
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client,
    comment,
    id_comment_for_args,
    id_news_for_args,
    form_data
):
    url = reverse('news:edit', args=id_comment_for_args)
    news_url = reverse('news:detail', args=id_news_for_args)
    url_to_comments = news_url + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_delete_comment_of_another_user(
        not_author_client, id_comment_for_args
):
    url = reverse('news:delete', args=id_comment_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_edit_comment_of_another_user(
        not_author_client, id_comment_for_args, form_data, comment
):
    url = reverse('news:edit', args=id_comment_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
