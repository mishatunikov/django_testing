from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    author = django_user_model.objects.create(username="author")
    return author


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username="reader")


@pytest.fixture
def not_author_client(client, not_author):
    client.force_login(not_author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(title="title", text="text")
    return news


@pytest.fixture
def id_news_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(text="comment", author=author, news=news)
    return comment


@pytest.fixture
def id_comment_for_args(comment):
    return (comment.id,)


@pytest.fixture
def count_news_on_page():
    return NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def create_news(author, count_news_on_page):
    today = timezone.now().date()
    news_list = [
        News(
            title=f"title {index}",
            text=f"text {index}",
            date=today + timedelta(days=index),
        )
        for index in range(count_news_on_page + 1)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def create_comments(author, news):
    comment_on_page = NEWS_COUNT_ON_HOME_PAGE
    today = timezone.now().date()
    for index in range(comment_on_page):
        comment = Comment(text="comment", author=author, news=news)
        comment.created = today + timedelta(days=index)
        comment.save()


@pytest.fixture
def home_page_url():
    url = reverse("news:home")
    return url


@pytest.fixture
def detail_news_url(id_news_for_args):
    url = reverse("news:detail", args=id_news_for_args)
    return url


@pytest.fixture
def form_data():
    return {"text": "new_text"}


@pytest.fixture
def comment_edit_url(id_comment_for_args):
    return reverse("news:edit", args=id_comment_for_args)


@pytest.fixture
def comment_delete_url(id_comment_for_args):
    return reverse("news:delete", args=id_comment_for_args)
