from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def author_client(author):
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='reader')


@pytest.fixture
def not_author_client(not_author):
    not_author_client = Client()
    not_author_client.force_login(not_author)
    return not_author_client


@pytest.fixture
def news(author):
    return News.objects.create(title='title', text='text')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(text='comment', author=author, news=news)


@pytest.fixture
def create_news(author):
    today = timezone.now().date()

    News.objects.bulk_create(
        News(
            title=f'title {index}',
            text=f'text {index}',
            date=today + timedelta(days=index),
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def create_comments(author, news):
    comment_on_page = 5
    today = timezone.now().date()
    for index in range(comment_on_page):
        comment = Comment(text='comment', author=author, news=news)
        comment.created = today + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'new_text'}


# urls.
@pytest.fixture
def home_page_url():
    return reverse('news:home')


@pytest.fixture
def detail_news_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
