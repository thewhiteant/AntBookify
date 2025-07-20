from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(200))
    chapters = db.relationship('Chapter', backref='book', cascade="all, delete-orphan")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    notes = db.relationship('Note', backref='chapter', cascade="all, delete-orphan")

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

@app.route("/")
def books():
    books = Book.query.all()
    return render_template("books.html", books=books)

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        thumbnail = request.form["thumbnail"]
        if title:
            new_book = Book(title=title, thumbnail=thumbnail)
            db.session.add(new_book)
            db.session.commit()
            flash("Book added successfully!")
            return redirect(url_for('books'))
        flash("Title is required.")
    return render_template("add_book.html")

@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == "POST":
        title = request.form["title"]
        thumbnail = request.form["thumbnail"]
        if title:
            book.title = title
            book.thumbnail = thumbnail
            db.session.commit()
            flash("Book updated!")
            return redirect(url_for('books'))
        flash("Title is required.")
    return render_template("edit_book.html", book=book)

@app.route("/delete_book/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted.")
    return redirect(url_for('books'))

@app.route("/book/<int:book_id>")
def chapters(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template("chapters.html", book=book, chapters=book.chapters)

@app.route("/add_chapter/<int:book_id>", methods=["GET", "POST"])
def add_chapter(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == "POST":
        title = request.form["title"]
        if title:
            chapter = Chapter(title=title, book_id=book_id)
            db.session.add(chapter)
            db.session.commit()
            flash("Chapter added!")
            return redirect(url_for("chapters", book_id=book_id))
        flash("Chapter title required.")
    return render_template("add_chapter.html", book=book)

@app.route("/edit_chapter/<int:chapter_id>", methods=["GET", "POST"])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == "POST":
        title = request.form["title"]
        if title:
            chapter.title = title
            db.session.commit()
            flash("Chapter updated!")
            return redirect(url_for("chapters", book_id=chapter.book_id))
        flash("Title required.")
    return render_template("edit_chapter.html", chapter=chapter)

@app.route("/delete_chapter/<int:chapter_id>", methods=["POST"])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    book_id = chapter.book_id
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted.")
    return redirect(url_for("chapters", book_id=book_id))

@app.route("/chapter/<int:chapter_id>")
def notes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template("notes.html", chapter=chapter, notes=chapter.notes)

@app.route("/add_note/<int:chapter_id>", methods=["GET", "POST"])
def add_note(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        if title and content:
            note = Note(title=title, content=content, chapter_id=chapter_id)
            db.session.add(note)
            db.session.commit()
            flash("Note added.")
            return redirect(url_for("notes", chapter_id=chapter_id))
        flash("All fields required.")
    return render_template("add_note.html", chapter=chapter)

@app.route("/edit_note/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        if title and content:
            note.title = title
            note.content = content
            db.session.commit()
            flash("Note updated.")
            return redirect(url_for("notes", chapter_id=note.chapter_id))
        flash("All fields required.")
    return render_template("edit_note.html", note=note)

@app.route("/delete_note/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    chapter_id = note.chapter_id
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted.")
    return redirect(url_for("notes", chapter_id=chapter_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
