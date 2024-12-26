from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    FORM_DATA = {'title': 'new_title', 'text': 'new_text', 'slug': 'new_slug'}
    FORM_DATA_WITHOUT_SLUG = {
        key: value for key, value in FORM_DATA.items() if key != 'slug'
    }
    NOTE_CREATION_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='username')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_user_can_create_note(self):
        response = self.author_client.post(
            self.NOTE_CREATION_URL,
            data=self.FORM_DATA
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.FORM_DATA['title'])
        self.assertEqual(new_note.text, self.FORM_DATA['text'])
        self.assertEqual(new_note.slug, self.FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_cant_create_note(self):
        login_url = reverse('users:login') + '?next=' + self.NOTE_CREATION_URL
        response = self.client.post(self.NOTE_CREATION_URL,
                                    data=self.FORM_DATA)
        self.assertRedirects(response, login_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        note = Note.objects.create(
            title='title', text='text', slug='slug', author=self.author
        )
        self.FORM_DATA['slug'] = note.slug
        response = self.author_client.post(self.NOTE_CREATION_URL,
                                           data=self.FORM_DATA)
        self.assertFormError(
            response, 'form', 'slug', errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_automatic_creation(self):
        response = self.author_client.post(
            self.NOTE_CREATION_URL, data=self.FORM_DATA_WITHOUT_SLUG
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        new_note = Note.objects.get()
        expected_slug = slugify(
            new_note.title)[:new_note._meta.get_field('slug').max_length]
        self.assertEqual(expected_slug, new_note.slug)


class TestNoteEditDelete(TestCase):

    SUCCESS_URL = reverse('notes:success')
    FORM_DATA = {'title': 'new_title', 'text': 'text', 'slug': 'slug'}

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.user = User.objects.create_user(username='user')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title='title', text='test', slug='slug', author=cls.author
        )
        cls.note_edit = reverse('notes:edit', args=(cls.note.slug, ))
        cls.note_delete = reverse('notes:delete',
                                  args=(cls.note.slug,))

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.note_edit, data=self.FORM_DATA)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.FORM_DATA['title'])
        self.assertEqual(self.note.text, self.FORM_DATA['text'])
        self.assertEqual(self.note.slug, self.FORM_DATA['slug'])

    def test_user_can_edit_another_user_note(self):
        response = self.user_client.post(self.note_edit, data=self.FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.note.title)
        self.assertEqual(self.note.text, self.note.text)
        self.assertEqual(self.note.slug, self.note.slug)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.note_delete)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_delete_note_another_user(self):
        response = self.user_client.delete(self.note_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
