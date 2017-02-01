import string
import sqlite3
from flask import Flask, g, render_template, render_template_string, request


app = Flask(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE_NAME'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.route('/form', methods=['GET', 'POST'])
def form():
    context = {
        'errors': {}
    }
    if request.method == 'GET':
        return render_template('form.html', **context)
    elif request.method == 'POST':
        form_fields = ['title', 'isbn', 'author']

        for field in form_fields:
            context[field] = request.form[field]

        # Validate Title
        if not context['title']:
            context['errors']['title'] = 'Title field must not be empty.'

        # Validate Author
        if not context['author'] or any(char.isdigit() for char in context['author']):
            context['errors']['author'] = 'Author name can not be empty or contain digits.'

        # Validate ISBN
        if not len(context['isbn']) == 13 or not context['isbn'].isdigit():
            context['errors']['isbn'] = 'ISBN must contain exactly 13 digits.'

        if context['errors']:
            return render_template('form.html', **context)

        # Save book in the database
        # Check if given author already exists. If not, insert it into the DB
        query = 'SELECT id FROM author WHERE name=:name;'
        params = {'name': context['author']}
        cursor = g.db.execute(query, params)
        author = cursor.fetchone()
        if not author:
            query = 'INSERT INTO author ("name") VALUES (:name);'
            params = {'name': context['author']}
            cursor = g.db.execute(query, params)
            author_id = cursor.lastrowid
            g.db.commit()
        else:
            author_id = author[0]

        # Insert book into the DB
        query_2 = 'INSERT INTO book ("title", "isbn", "author_id") VALUES (:title, :isbn, :author_id);'
        params_2 = {
            'title': context['title'],
            'isbn': context['isbn'],
            'author_id': author_id
        }
        try:
            g.db.execute(query_2, params_2)
            g.db.commit()
        except sqlite3.IntegrityError:
            flash('Something went wrong while saving your request data', 'danger')
        context['message'] = 'Book successfully saved!'

        # Clear form input values
        for field in form_fields:
            context[field] = ''

    return render_template('form.html', **context)


@app.route('/books')
def books():
    context = {}
    cursor = g.db.execute("""
        SELECT b.title, a.name, b.isbn
        FROM book b INNER JOIN author a ON b.author_id = a.id;
    """)
    context['books'] = [{'title': row[0], 'author': row[1], 'isbn': row[2]}
                        for row in cursor.fetchall()]
    return render_template('books.html', **context)
