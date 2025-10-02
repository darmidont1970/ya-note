from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from notes.models import Note

User = get_user_model()


class RoutesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок1',
            text='Текст1',
            slug='note_slug1',
            author=cls.author
        )
        cls.urls = {
            'home': reverse('notes:home'),
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'detail': reverse('notes:detail', kwargs={'slug': cls.note.slug}),
            'edit': reverse('notes:edit', kwargs={'slug': cls.note.slug}),
            'delete': reverse('notes:delete', kwargs={'slug': cls.note.slug}),
            'success': reverse('notes:success'),
            'login': reverse('users:login'),
            'logout': reverse('users:logout'),
            'signup': reverse('users:signup'),
        }

    def setUp(self):
        """Create clients: author and reader."""
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_status_codes(self):
        """Check response codes."""
        cases = (
            (self.urls['home'], self.client, HTTPStatus.OK),
            (self.urls['home'], self.reader_client, HTTPStatus.OK),
            (self.urls['list'], self.reader_client, HTTPStatus.OK),
            (self.urls['list'], self.author_client, HTTPStatus.OK),
            (self.urls['detail'], self.reader_client, HTTPStatus.NOT_FOUND),
            (self.urls['detail'], self.author_client, HTTPStatus.OK),
            (self.urls['add'], self.reader_client, HTTPStatus.OK),
            (self.urls['edit'], self.reader_client, HTTPStatus.NOT_FOUND),
            (self.urls['edit'], self.author_client, HTTPStatus.OK),
            (self.urls['delete'], self.reader_client, HTTPStatus.NOT_FOUND),
            (self.urls['delete'], self.author_client, HTTPStatus.OK),
            (self.urls['login'], self.client, HTTPStatus.OK),
            (self.urls['signup'], self.client, HTTPStatus.OK),
            (self.urls['logout'], self.reader_client, HTTPStatus.OK),
        )
        for url, client, expected in cases:
            with self.subTest(url=url, client=client):
                if url == self.urls['logout']:
                    response = client.post(url)
                else:
                    response = client.get(url)
                self.assertEqual(response.status_code, expected)

    def test_anonymous_redirects(self):
        """Check that anonymous users are redirected to the login."""
        login_url = self.urls['login']
        protected_urls = (
            self.urls['list'],
            self.urls['detail'],
            self.urls['add'],
            self.urls['edit'],
            self.urls['delete'],
        )
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                expected_redirect = f'{login_url}?next={url}'
                self.assertRedirects(response, expected_redirect)
