import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model

from news.forms import CommentForm
from .conftest import NEWS_COUNT_ON_HOME_PAGE

User = get_user_model()


@pytest.mark.django_db
def test_count_of_news_in_home_page(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count is NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_order_of_news_in_home_page(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, all_comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(admin_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = admin_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
