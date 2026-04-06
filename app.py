from flask import Flask, request, jsonify, session, render_template # Added render_template here
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import redirect
import os
# -- Code below is to convert user response to embedded value
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load the AI model and the embeddings once when the server starts
model = SentenceTransformer('all-MiniLM-L6-v2')
with open('book_embeddings.pkl', 'rb') as f:
    data = pickle.load(f)
    book_ids = data['book_ids']
    book_embeddings = data['embeddings']

app = Flask(__name__) # This tells Flask to look for static/templates in the current folder

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recobook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

# --- USER MODEL ---
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    authors = db.Column(db.String(255))
    genres = db.Column(db.Text)
    description = db.Column(db.Text)

# 1. Create a full Class for the Bookmark
class Bookmark(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), primary_key=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow) # This captures the date

    # Relationships to easily get the Book or User object
    book = db.relationship("Book", backref="saved_by_users")
    user = db.relationship("User", backref="my_bookmarks")

# 2. In your User class, you can now remove the old relationship.
# Your User class will now automatically have 'my_bookmarks' 
# because of the 'backref' in the Bookmark class above.

# After adding this, run app.py once to create the table

# --- INITIALIZE DATABASE ---
with app.app_context():
    db.create_all()

# --- HTML PAGE ROUTES (MOVED UP) ---
@app.route('/')
def home():
    if 'user_id' not in session:
        # If not logged in, send them back to the login page
        return redirect('/login_page')
    
    # NEW: Fetch the user from the database using their session ID
    current_user = User.query.get(session['user_id'])
    
    # NEW: Pass their name to the HTML template
    return render_template('home.html', user_name=current_user.name)

@app.route('/quiz_page')
def quiz_page():
    if 'user_id' not in session:
        return redirect('/login_page')
    return render_template('quiz.html')

@app.route('/bookmarks_page')
def bookmarks_page():
    if 'user_id' not in session:
        return redirect('/login_page')
    
    # We query the Bookmark table directly to get the 'saved_at' property
    user_bookmarks = Bookmark.query.filter_by(user_id=session['user_id']).order_by(Bookmark.saved_at.desc()).all()
    return render_template('bookmarks.html', books=user_bookmarks)

@app.route('/api/bookmark/<int:book_id>', methods=['POST'])
def add_bookmark(book_id):
    if 'user_id' not in session:
        return jsonify({"message": "Please login first"}), 401
    
    # Check if it already exists
    existing = Bookmark.query.filter_by(user_id=session['user_id'], book_id=book_id).first()
    
    if not existing:
        new_bookmark = Bookmark(user_id=session['user_id'], book_id=book_id)
        db.session.add(new_bookmark)
        db.session.commit()
        return jsonify({"message": "Bookmarked successfully!"}), 200
    
    return jsonify({"message": "Already in your bookmarks"}), 200

@app.route('/api/bookmark/remove/<int:book_id>', methods=['DELETE'])
def remove_bookmark(book_id):
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401
    
    bookmark = Bookmark.query.filter_by(user_id=session['user_id'], book_id=book_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({"message": "Removed"}), 200
    return jsonify({"message": "Not found"}), 404

@app.route ('/searchbook_page')
def searchbook_page():
    if 'user_id' not in session:
        return redirect('/login_page')
    return render_template('search.html')

@app.route('/api/search', methods=['POST'])
def search_books():
    data = request.get_json()
    query = data.get('query', '')
    genre_filter = data.get('genre', '')

    # Base Query
    book_query = Book.query

    # 1. Apply Genre Filter if selected
    if genre_filter:
        book_query = book_query.filter(Book.genres.contains(genre_filter))

    # 2. Apply Search Logic
    if len(query) > 20:  # If user types a long "mood" or description, use AI
        user_vector = model.encode([query])
        similarities = cosine_similarity(user_vector, book_embeddings)[0]
        top_indices = np.argsort(similarities)[-10:][::-1]
        recommended_ids = [book_ids[i] for i in top_indices]
        
        # Get these specific books
        books = Book.query.filter(Book.book_id.in_(recommended_ids)).all()
    else:
        # Standard search for Title or Author
        books = book_query.filter(
            (Book.title.contains(query)) | (Book.authors.contains(query))
        ).limit(20).all()

    results = []
    for book in books:
        results.append({
            "book_id": book.book_id,
            "title": book.title,
            "authors": book.authors,
            "genres": book.genres
        })
    
    return jsonify(results)

@app.route('/profile_page')
def profile_page():
    if 'user_id' not in session:
        return redirect('/login_page')
    
    # Fetch the real user data
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear() # This removes 'user_id' and logs the user out
    return redirect('/login_page')

@app.after_request
def add_header(response):
    # This tells the browser to NOT cache the page
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route ('/result_page')
def result_page():
    if 'user_id' not in session:
        return redirect('/login_page')
    return render_template('result.html')

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    user_query = data.get('quiz_text')

    # Vectorize and calculate similarity
    user_vector = model.encode([user_query])
    similarities = cosine_similarity(user_vector, book_embeddings)[0]

    # Get Top 5
    top_indices = np.argsort(similarities)[-5:][::-1]
    recommended_ids = [book_ids[i] for i in top_indices]
    
    # Fetch from DB
    recommended_books = Book.query.filter(Book.book_id.in_(recommended_ids)).all()
    
    # Sort the DB results to match the similarity order
    book_dict = {book.book_id: book for book in recommended_books}
    
    results = []
    for i in top_indices:
        book_id = book_ids[i]
        book = book_dict.get(book_id)
        if book:
            results.append({
                "book_id": book.book_id, # Make sure this line exists!
                "title": book.title,
                "authors": book.authors,
                "match_score": float(similarities[i]) # This is the key line!
            })
    
    return jsonify(results)


@app.route('/details/<int:book_id>')
def details_page(book_id):
    if 'user_id' not in session:
        return redirect('/login_page')
    
    # Fetch the specific book by its ID
    book = Book.query.get_or_404(book_id)
    return render_template('details.html', book=book)

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

# --- AUTH API ROUTES ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already exists"}), 400
    
    new_user = User(name=data['name'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration successful"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        # 1. Update the role in the database
        if user.email == 'michael@admin.com': 
            user.role = 'admin'
            db.session.commit()
            # Refresh the user object from the database to be 100% sure
            db.session.refresh(user) 

        # 2. Save info to session (Now using the updated role)
        session['user_id'] = user.user_id
        session['role'] = user.role 
        
        # 3. Use the session role for the redirect logic
        if session.get('role') == 'admin':
            return jsonify({"message": "Admin login successful", "redirect": "/admin_dashboard"}), 200
        else:
            return jsonify({"message": "Login successful", "redirect": "/"}), 200
            
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/admin_dashboard')
def admin_dashboard():
    # Security check: Are you logged in? Are you an admin?
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login_page')
    
    # Fetch books to show in the admin table
    all_books = Book.query.order_by(Book.book_id.desc()).limit(100).all()
    return render_template('admin.html', books=all_books)

if __name__ == '__main__':
    app.run(debug=True)