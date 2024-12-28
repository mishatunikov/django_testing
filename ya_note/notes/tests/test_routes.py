from http import HTTPStatus

from django.test import Client
from django.contrib.auth import get_user_model, get_user

from notes.tests.common import TestBaseClass, URLS


User = get_user_model()


class RoutesTest(TestBaseClass):

    def test_access_pages(self):
        client_urls_expected_status = (
            (Client(), URLS['home'], HTTPStatus.OK),
            (Client(), URLS['login'], HTTPStatus.OK),
            (Client(), URLS['logout'], HTTPStatus.OK),
            (Client(), URLS['signup'], HTTPStatus.OK),
            (self.author_client, URLS['notes_list'], HTTPStatus.OK),
            (self.author_client, URLS['success_note'], HTTPStatus.OK),
            (self.author_client, URLS['add_note'], HTTPStatus.OK),
            (self.author_client, URLS['delete_note'], HTTPStatus.OK),
            (self.author_client, URLS['edit_note'], HTTPStatus.OK),
            (
                self.not_author_client,
                URLS['delete_note'],
                HTTPStatus.NOT_FOUND,
            ),
            (self.not_author_client, URLS['edit_note'], HTTPStatus.NOT_FOUND),
        )

        for (
            parametrized_client,
            url,
            expected_status,
        ) in client_urls_expected_status:
            with self.subTest(
                username=get_user(parametrized_client).username,
                url=url,
                expected_status=expected_status,
            ):
                response = parametrized_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):

        urls = (
            URLS['notes_detail'],
            URLS['delete_note'],
            URLS['edit_note'],
            URLS['notes_list'],
            URLS['add_note'],
            URLS['success_note'],
        )

        for url in urls:
            with self.subTest(urls=url):
                redirect_url = f'{URLS["login"]}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
