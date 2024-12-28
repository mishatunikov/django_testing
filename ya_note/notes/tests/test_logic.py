from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.common import TestBaseClass, URLS


User = get_user_model()


class TestNoteCreation(TestBaseClass):

    FORM_DATA = {'title': 'new_title', 'text': 'new_text', 'slug': 'new_slug'}
    FORM_DATA_WITHOUT_SLUG = {
        key: value for key, value in FORM_DATA.items() if key != 'slug'
    }
    NOTE_CREATION_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(
            self.NOTE_CREATION_URL, data=self.FORM_DATA
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.FORM_DATA['title'])
        self.assertEqual(new_note.text, self.FORM_DATA['text'])
        self.assertEqual(new_note.slug, self.FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_cant_create_note(self):
        initial_count_notes = Note.objects.count()
        login_url = reverse('users:login') + '?next=' + self.NOTE_CREATION_URL
        response = self.client.post(
            self.NOTE_CREATION_URL, data=self.FORM_DATA
        )
        self.assertRedirects(response, login_url)
        self.assertEqual(Note.objects.count(), initial_count_notes)

    def test_not_unique_slug(self):
        self.FORM_DATA['slug'] = self.note.slug
        response = self.author_client.post(
            self.NOTE_CREATION_URL, data=self.FORM_DATA
        )
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_automatic_creation(self):
        response = self.author_client.post(
            self.NOTE_CREATION_URL, data=self.FORM_DATA_WITHOUT_SLUG
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        new_note = Note.objects.last()
        expected_slug = slugify(new_note.title)[
            : new_note._meta.get_field('slug').max_length
        ]
        self.assertEqual(expected_slug, new_note.slug)


class TestNoteEditDelete(TestBaseClass):

    SUCCESS_URL = reverse('notes:success')
    FORM_DATA = {'title': 'new_title', 'text': 'text', 'slug': 'slug'}

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            URLS['edit_note'], data=self.FORM_DATA
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.FORM_DATA['title'])
        self.assertEqual(self.note.text, self.FORM_DATA['text'])
        self.assertEqual(self.note.slug, self.FORM_DATA['slug'])

    def test_user_cant_edit_another_user_note(self):
        response = self.not_author_client.post(
            URLS['edit_note'], data=self.FORM_DATA
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.author)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(URLS['delete_note'])
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_another_user(self):
        response = self.not_author_client.delete(URLS['delete_note'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
