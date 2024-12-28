from http import HTTPStatus

import pytest
from django.test import Client
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


URLS = {
    'home_page': lazy_fixture('home_page_url'),
    'detail_news': lazy_fixture('detail_news_url'),
    'comment_edit': lazy_fixture('comment_edit_url'),
    'comment_delete': lazy_fixture('comment_delete_url'),
    'login': lazy_fixture('login_url'),
    'logout': lazy_fixture('logout_url'),
    'signup': lazy_fixture('signup_url'),
}

AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')


@pytest.mark.parametrize(
    'parametrized_client, url, expected_status',
    (
        (Client(), URLS['home_page'], HTTPStatus.OK),
        (Client(), URLS['detail_news'], HTTPStatus.OK),
        (Client(), URLS['login'], HTTPStatus.OK),
        (Client(), URLS['logout'], HTTPStatus.OK),
        (Client(), URLS['signup'], HTTPStatus.OK),
        (AUTHOR_CLIENT, URLS['comment_edit'], HTTPStatus.OK),
        (AUTHOR_CLIENT, URLS['comment_delete'], HTTPStatus.OK),
        (NOT_AUTHOR_CLIENT, URLS['comment_edit'], HTTPStatus.NOT_FOUND),
        (NOT_AUTHOR_CLIENT, URLS['comment_delete'], HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability(url, parametrized_client, expected_status):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        URLS['comment_edit'],
        URLS['comment_delete'],
    ),
)
def test_redirect_for_anonymous_user(client, url, login_url):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
