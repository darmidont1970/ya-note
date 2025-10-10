from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from http import HTTPStatus

from notes.models import Note
from notes.forms import NoteForm

"""Test content class."""

User = get_user_model()


class NoteVisibilityTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.other_user = User.objects.create_user(username='Мимо проходил')
        cls.note = Note.objects.create(
            title='Тест Заметка',
            text='Просто текст.',
            author=cls.author
        )

    def test_note_in_object_list(self):
        """A single note is passed to the object_list on the list page."""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.note, response.context['object_list'])

    def test_note_is_not_visible_to_non_author(self):
        """If the note is not the author's, the note should not be shown."""
        self.client.force_login(self.other_user)
        response = self.client.get(reverse(
            'notes:detail',
            kwargs={'slug': self.note.slug}
        ))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_note_is_visible_to_author(self):
        """The note should be shown to the author."""
        self.client.force_login(self.author)
        response = self.client.get(reverse(
            'notes:detail',
            kwargs={'slug': self.note.slug}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_add_note_form(self):
        """
        Testing the display of the form for adding a note on the page
        by an author(authorized user).
        """
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_author_edit_note_form(self):
        """
        Testing the display of the note editing form on the page
        by an author(authorized user).
        """        
        self.client.force_login(self.author)
        response = self.client.get(reverse(
            'notes:edit',
            kwargs={'slug': self.note.slug}
        ))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
