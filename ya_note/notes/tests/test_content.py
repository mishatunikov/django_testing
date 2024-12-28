from django.test import Client
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.common import TestBaseClass, URLS

User = get_user_model()


class TestListNotesPage(TestBaseClass):

    def test_notes_list_for_different_users(self):
        user_client_and_flag = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for user_client, flag in user_client_and_flag:
            with self.subTest(client=user_client, note=self.note, flag=flag):
                url = URLS['notes_list']
                response = user_client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, flag)


class TestNotesForm(TestBaseClass):
    urls = (
        URLS['add_note'],
        URLS['edit_note'],
    )

    def test_notes_form_on_page(self):
        for url in self.urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)

    def test_anonymous_has_not_form(self):
        for url in self.urls:
            with self.subTest(url=url):
                response = Client().get(url)
                self.assertEqual(response.context, None)
