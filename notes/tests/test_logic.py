from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class NoteCreationTest(TestCase):
    """Note creation test class."""

    NOTE_TITLE = 'Тест Заметка'
    NOTE_TEXT = 'Просто текст.'
    NOTE_SLUG = 'note1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.url = reverse('notes:add')

    def test_author_create_note(self):
        """Creating a note works correctly."""
        self.client.force_login(self.author)
        form_data = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'slug': self.NOTE_SLUG,
            'author': self.author
        }
        self.client.post(self.url, form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_author_create_note_without_slug(self):
        """Checking if a note was created without a slug."""
        self.client.force_login(self.author)
        form_data = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'author': self.author
        }
        self.client.post(self.url, form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertIsNotNone(note.slug)

    def test_anonymous_user_cannot_create_note(self):
        """Anonymous cannot create a note."""
        form_data = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'slug': self.NOTE_SLUG
        }
        response = self.client.post(self.url, form_data)
        self.assertRedirects(response, '/auth/login/?next=' + self.url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_create_note_with_duplicate_slug(self):
        """Attempt to create a note with the same slug."""
        form_data = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'slug': self.NOTE_SLUG,
            'author': self.author
        }
        Note.objects.create(**form_data)
        self.client.force_login(self.author)
        self.client.post(self.url, form_data)
        self.assertEqual(Note.objects.filter(slug=self.NOTE_SLUG).count(), 1)


class NoteEditingTest(TestCase):
    """Note editing test class."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тест Заметка',
            text='Просто текст.',
            slug='note1',
            author=cls.author
        )

    def test_author_can_edit_note(self):
        """The author can edit his note."""
        self.client.force_login(self.author)
        new_title = 'Изменена Заметка'
        new_text = 'Другой текст.'
        new_slug = 'note2'
        self.client.post(
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            {
                'title': new_title,
                'text': new_text,
                'slug': new_slug
            }
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, new_title)
        self.assertEqual(self.note.text, new_text)
        self.assertEqual(self.note.slug, new_slug)

    def test_author_can_delete_note(self):
        """The author can delete his note."""
        self.client.force_login(self.author)
        response = self.client.post(reverse(
            'notes:delete',
            kwargs={'slug': self.note.slug}
        ))
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)


class NonAuthorsNoteEditingTest(TestCase):

    NOTE_TITLE = 'Тест Заметка'
    NOTE_TEXT = 'Просто текст.'
    NOTE_SLUG = 'note1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.non_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

    def test_non_author_cannot_edit_note(self):
        self.client.force_login(self.non_author)
        self.client.post(
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            {
                'title': 'Изменена Заметка',
                'text': 'Другой текст.',
                'slug': 'note2'
            }
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)

    def test_non_author_cannot_delete_note(self):
        self.client.force_login(self.non_author)
        self.client.post(reverse(
            'notes:delete',
            kwargs={'slug': self.note.slug}
        ))
        self.assertEqual(Note.objects.count(), 1)
