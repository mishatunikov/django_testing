from http import HTTPStatus

from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


def test_anonymous_cant_create_comment(client, detail_news_url, form_data):
    login_url = reverse("users:login")
    expected_url = f"{login_url}?next={detail_news_url}"
    response = client.post(detail_news_url, data=form_data)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, detail_news_url, form_data):
    response = author_client.post(detail_news_url, data=form_data)
    assertRedirects(response, detail_news_url + "#comments")
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(author_client, detail_news_url, form_data):
    form_data["text"] = BAD_WORDS[0]
    response = author_client.post(detail_news_url, data=form_data)
    assertFormError(response, "form", "text", errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        comment_edit_url, author_client, form_data, detail_news_url,
        comment, author
):
    response = author_client.post(comment_edit_url, data=form_data)
    assertRedirects(response, detail_news_url + "#comments")
    comment.refresh_from_db()
    assert comment.text == form_data["text"]
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
    comment_delete_url, author_client, form_data, detail_news_url
):
    response = author_client.post(comment_delete_url, data=form_data)
    assertRedirects(response, detail_news_url + "#comments")
    assert Comment.objects.count() == 0


def test_not_author_cant_delete_comment(
    comment_delete_url, not_author_client, form_data
):
    response = not_author_client.post(comment_delete_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
