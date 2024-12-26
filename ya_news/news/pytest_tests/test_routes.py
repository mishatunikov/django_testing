from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, args",
    (
        ("news:home", None),
        ("news:detail", pytest.lazy_fixture("id_news_for_args")),
        ("users:login", None),
        ("users:logout", None),
        ("users:signup", None),
    ),
)
def test_home_availability_for_anonymous_user(name, args, client):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (pytest.lazy_fixture("not_author_client"), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    "name",
    (
        "news:edit",
        "news:delete",
    ),
)
def test_edit_delete_comment_for_users(
    parametrized_client, expected_status, name, id_comment_for_args
):
    url = reverse(name, args=id_comment_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "name",
    (
        "news:edit",
        "news:delete",
    ),
)
def test_redirect_for_anonymous_user(client, name, id_comment_for_args):
    login = reverse("users:login")
    url = reverse(name, args=id_comment_for_args)
    expected_url = f"{login}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
