from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_cant_create_comment(
    client, detail_news_url, login_url, form_data
):
    initial_comment_count = Comment.objects.count()
    expected_url = f'{login_url}?next={detail_news_url}'
    response = client.post(detail_news_url, data=form_data)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_comment_count


def test_user_can_create_comment(author_client, detail_news_url, form_data):
    Comment.objects.all().delete()
    response = author_client.post(detail_news_url, data=form_data)
    assertRedirects(response, detail_news_url + '#comments')
    assert Comment.objects.count() == 1


@pytest.mark.parametrize('forbidden_word', BAD_WORDS)
def test_user_cant_use_bad_words(
    author_client, detail_news_url, form_data, forbidden_word
):
    form_data['text'] = forbidden_word
    response = author_client.post(detail_news_url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    comment_edit_url,
    author_client,
    form_data,
    detail_news_url,
    comment,
    author,
):
    response = author_client.post(comment_edit_url, data=form_data)
    assertRedirects(response, detail_news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author


def test_not_author_cant_edit_comment(
    comment_edit_url, not_author_client, form_data, comment
):
    response = not_author_client.post(comment_edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text


def test_author_can_delete_comment(
    comment_delete_url, author_client, form_data, detail_news_url, comment
):
    initial_comment_count = Comment.objects.count()
    response = author_client.post(comment_delete_url, data=form_data)
    assertRedirects(response, detail_news_url + '#comments')
    assert Comment.objects.count() == initial_comment_count - 1
    assert not Comment.objects.filter(id=comment.id).exists()


def test_not_author_cant_delete_comment(
    comment_delete_url, not_author_client, form_data, comment
):
    initial_comment_count = Comment.objects.count()
    response = not_author_client.post(comment_delete_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comment_count
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
