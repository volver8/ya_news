import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_news(client, news, form_data):
    """Проверка POST-запросов от анонимуса на добавление комментариев"""
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author, author_client, news, form_data):
    """Проверка POST-запросов от автора на добавление комментариев"""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_are_bad_words_in_comment(admin_client, news, form_data):
    """Проверка блокировки стоп-слов"""
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = admin_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client,
    form_data,
    comment,
    url_to_comments
):
    """Проверка редактирования своего комментария."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_other_user_cant_edit_note(
    not_author_client,
    form_data,
    comment
):
    """Проверка редактирования чужого комментария."""
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, url_to_comments):
    """Проверка удаления своего комментария."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cant_delete_comment(not_author_client, comment):
    """Проверка удаления чужого комментария."""
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
