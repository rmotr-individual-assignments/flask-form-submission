import os
import sqlite3
import unittest

from app import app


TESTING_DATABASE_NAME = 'test_library.db'
app.config.update({
    'DATABASE_NAME': TESTING_DATABASE_NAME
})


class LibraryTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = sqlite3.connect(TESTING_DATABASE_NAME)
        cls.db.execute("CREATE TABLE book (id integer primary key autoincrement, title text, isbn text, author_id integer)")
        cls.db.execute("CREATE TABLE author (id integer primary key autoincrement, name text)")
        cls.db.commit()

    def setUp(self):
        self.app = app.test_client()
        # Reset book and author tables BEFORE every test.
        self.db.execute("DELETE FROM book;")
        self.db.execute("DELETE FROM author;")
        self.db.commit()

    @classmethod
    def tearDownClass(cls):
        os.remove(TESTING_DATABASE_NAME)

    def test_create_book(self):
        """Should create a book and its author when given data is valid"""
        # Preconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])
        cursor = self.db.execute("SELECT * FROM author;")
        self.assertEqual(cursor.fetchall(), [])

        payload = {
            'title': 'The Aleph',
            'author': 'Jorge Luis Borges',
            'isbn': '1234567891234'
        }
        self.app.post('/form', data=payload)

        # Postconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [(1, 'The Aleph', '1234567891234', 1)])
        cursor = self.db.execute("SELECT * FROM author;")
        self.assertEqual(cursor.fetchall(), [(1, u'Jorge Luis Borges')])

    def test_create_book_missing_title(self):
        """Should not create a book when title is missing"""
        # Preconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

        payload = {
            'author': 'Jorge Luis Borges',
            'isbn': '1234567891234'
        }
        self.app.post('/form', data=payload)

        # Postconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

    def test_create_book_missing_author(self):
        """Should not create a book when author is missing"""
        # Preconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

        payload = {
            'title': 'The Aleph',
            'isbn': '1234567891234'
        }
        self.app.post('/form', data=payload)

        # Postconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

    def test_create_book_missing_isbn(self):
        """Should not create a book when ISBN is missing"""
        # Preconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

        payload = {
            'title': 'The Aleph',
            'author': 'Jorge Luis Borges'
        }
        self.app.post('/form', data=payload)

        # Postconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

    def test_create_book_invalid_isbn(self):
        """Should not create a book when ISBN doesnt have exactly 13 digits"""
        # Preconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

        payload = {
            'title': 'The Aleph',
            'author': 'Jorge Luis Borges',
            'isbn': '1234'
        }
        self.app.post('/form', data=payload)

        # Postconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

    def test_create_book_invalid_author(self):
        """Should not create a book when authors name contains digits or symbols"""
        # Preconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

        payload = {
            'title': 'The Aleph',
            'author': 'Jorge Luis Borges 123!',
            'isbn': '1234567891234'
        }
        self.app.post('/form', data=payload)

        # Postconditions
        cursor = self.db.execute("SELECT * FROM book;")
        self.assertEqual(cursor.fetchall(), [])

    def test_list_books(self):
        """Should return the list of all books in the database"""
        # Preconditions
        payload = {
            'title': 'The Aleph',
            'author': 'Jorge Luis Borges',
            'isbn': '1234567891234'
        }
        self.app.post('/form', data=payload)

        response = self.app.get('/books')

        # Postconditions
        self.assertTrue('<th>The Aleph</th>' in response.data)
        self.assertTrue('<th>Jorge Luis Borges</th>' in response.data)
        self.assertTrue('<th>1234567891234</th>' in response.data)


if __name__ == '__main__':
    unittest.main()
