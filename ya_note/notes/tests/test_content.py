from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestListNotesPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='not_author')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(
            text='text',
            title='title',
            slug='slug',
            author=cls.author
        )
        cls.note.save()

    def test_notes_list_for_different_users(self):
        user_client_and_flag = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for user_client, flag in user_client_and_flag:
            with self.subTest(client=user_client, note=self.note, flag=flag):
                url = reverse('notes:list')
                response = user_client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, flag)


class TestNotesForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            text='text',
            title='title',
            slug='slug',
            author=cls.user
        )

    def test_note_creation_form_on_page(self):
        url = reverse('notes:add')
        response = self.user_client.get(url)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, NoteForm)

    def test_note_update_form_on_page(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.user_client.get(url)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, NoteForm)
