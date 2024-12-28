import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('create_news')
def test_count_news_on_main_page(client, home_page_url):
    response = client.get(home_page_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    assert object_list.count() == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('create_news')
def test_sort_news_on_main_page(client, home_page_url):
    response = client.get(home_page_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.usefixtures('create_comments')
def test_sort_comment_on_detail_news_page(client, detail_news_url):
    response = client.get(detail_news_url)
    assert 'news' in response.context
    news = response.context['news']
    comments = news.comment_set.all()
    all_dates = [comment.created for comment in comments]
    sorted_dates = sorted(all_dates)
    assert sorted_dates == all_dates


@pytest.mark.parametrize(
    'parametrized_client, form_exists',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
def test_comment_form_exists_for_users(
    parametrized_client, form_exists, detail_news_url
):
    response = parametrized_client.get(detail_news_url)
    context = response.context
    assert ('form' in context) == form_exists
    if form_exists:
        assert isinstance(context['form'], CommentForm)
