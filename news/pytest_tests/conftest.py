from datetime import datetime, timedelta
import pytest

from django.test.client import Client
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from news.models import News, Comment


NEWS_TITLE = 'Заголовок новости'
NEWS_TEXT = 'Текст новости'
NEW_NEWS_TITLE = 'Новый заголовок новости'
NEW_NEWS_TEXT = 'Новый текст новости'
COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Новый текст комментария'

NEWS_COUNT_ON_HOME_PAGE = 10


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title=NEWS_TITLE,
        text=NEWS_TEXT
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text=COMMENT_TEXT,
        author=author
    )
    return comment


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def all_comments(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'{COMMENT_TEXT} {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {
        'text': NEW_COMMENT_TEXT
    }


@pytest.fixture
def url_to_comments(news):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    return url_to_comments
