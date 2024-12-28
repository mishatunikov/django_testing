from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


SLUG = 'slug'
SLUG_FOR_ARGS = (SLUG,)
URLS = {
    'home': reverse('notes:home'),
    'notes_list': reverse('notes:list'),
    'notes_detail': reverse('notes:detail', args=SLUG_FOR_ARGS),
    'add_note': reverse('notes:add'),
    'edit_note': reverse('notes:edit', args=SLUG_FOR_ARGS),
    'delete_note': reverse('notes:delete', args=SLUG_FOR_ARGS),
    'success_note': reverse('notes:success'),
    'login': reverse('users:login'),
    'logout': reverse('users:logout'),
    'signup': reverse('users:signup'),
}

User = get_user_model()


class TestBaseClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create_user(username='not_author')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(
            text='text', title='title', slug=SLUG, author=cls.author
        )
