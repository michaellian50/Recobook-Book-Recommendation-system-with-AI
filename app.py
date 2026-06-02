from flask import Flask, request, jsonify, session, render_template, redirect, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
import pickle
import re
import numpy as np
import requests
import time
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()
# --- HUGGING FACE API CONFIG ---
# Remove /pipeline/feature-extraction/ as it is causing the 404
from huggingface_hub import InferenceClient

# FIX: Fetch the API key safely from environment variables instead of hardcoding it
hf_token = os.environ.get("HF_API_KEY")

# Fallback check to alert you in the terminal if you forgot to set the environment variable
if not hf_token:
    print("WARNING: 'HF_API_KEY' environment variable not found. Hugging Face requests may fail.")

# Initialize the client securely
client = InferenceClient(api_key=hf_token)

def query_hf_api(texts):
    try:
        # feature_extraction is the specific task for creating embeddings
        # It automatically handles the URL routing for you
        embeddings = client.feature_extraction(
            texts, 
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Convert to list if it returns a numpy array
        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()
        return embeddings

    except Exception as e:
        print(f"HF Inference Error: {str(e)}")
        return None

# Load the pre-calculated embeddings
with open('book_embeddings.pkl', 'rb') as f:
    data = pickle.load(f)
    book_ids = data['book_ids']
    book_embeddings = data['embeddings']

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recobook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

# --- MODELS ---
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    current_genre = db.Column(db.String(100), default="No profile detected")
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
    average_rating = db.Column(db.Float) 
    image_url = db.Column(db.String(500)) 

class Bookmark(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), primary_key=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    book = db.relationship("Book", backref="saved_by_users")
    user = db.relationship("User", backref="my_bookmarks")

with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    user_name = "Guest"
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
        user_name = current_user.name
    return render_template('home.html', user_name=user_name)

@app.route('/quiz_page')
def quiz_page():
    is_logged_in = 'user_id' in session
    user_name = User.query.get(session['user_id']).name if is_logged_in else "Guest"
    return render_template('quiz.html', user_name=user_name, is_logged_in=is_logged_in)

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    user_query = data.get('quiz_text')
    user_age = data.get('age')

    # 1. Get embedding from Hugging Face
    user_vector = query_hf_api([user_query])
    
    # 2. Robust Check: If API is warming up (503) or failed, user_vector will be None
    if user_vector is None or not isinstance(user_vector, list):
        return jsonify({"message": "AI model is warming up. Please wait 15 seconds and try again."}), 503

    try:
        # 3. Shape Handling: Ensure the vector is exactly 2D (1 row, 384 columns)
        # This fixes potential dimension errors during cosine_similarity
# Inside get_recommendations()
        user_vector_np = np.array(user_vector)

        # Force the shape to (1, 384) regardless of what the API spits out
        if user_vector_np.ndim == 1:
            user_vector_np = user_vector_np.reshape(1, -1)
        elif user_vector_np.ndim == 2:
            # If it's (1, 384), we are good. If it's (sequence_length, 384), mean pool it.
            if user_vector_np.shape[0] > 1:
                user_vector_np = np.mean(user_vector_np, axis=0).reshape(1, -1)

        # 4. Calculate similarity against your book_embeddings.pkl
        # similarities becomes a 1D array of scores for all books
        similarities = cosine_similarity(user_vector_np, book_embeddings)[0]

        # 5. Get top 50 matches to allow for filtering by age/genre afterwards
        top_indices = np.argsort(similarities)[-50:][::-1]
        candidate_ids = [book_ids[i] for i in top_indices]
        
        # 6. Database Filter: Fetch books that match the candidate IDs
        book_query = Book.query.filter(Book.book_id.in_(candidate_ids))
        
        # Apply age filter if necessary
        if user_age == 'ya':
            book_query = book_query.filter(Book.genres.contains('young-adult'))
        
        recommended_books = book_query.all()
        
        # Create a dictionary for fast lookup by ID
        book_dict = {book.book_id: book for book in recommended_books}
        
        results = []
        count = 0
        
        # 7. Final Selection: Build the top 12 results in order of similarity score
        for i in top_indices:
            if count >= 12: 
                break
            
            book_id = book_ids[i]
            book = book_dict.get(book_id)
            
            if book:
                results.append({
                    "book_id": book.book_id,
                    "title": book.title,
                    "authors": book.authors,
                    "match_score": float(similarities[i]),
                    "average_rating": book.average_rating,
                    "image_url": book.image_url
                })
                count += 1
        
        return jsonify(results)

    except Exception as e:
        # Log the error to your terminal so you can see why it failed
        print(f"Recommendation Error: {str(e)}")
        return jsonify({"message": "An error occurred while matching books."}), 500

@app.route('/api/search', methods=['POST'])
def search_books():
    data = request.get_json()
    query_text = data.get('query', '')
    genre_filter = data.get('genre', '')
    book_query = Book.query

    if genre_filter:
        book_query = book_query.filter(Book.genres.contains(genre_filter))

    # Semantic Vector Search for longer, descriptive queries
    if len(query_text) > 20: 
        user_vector = query_hf_api([query_text])
        
        # Robust Check: If API is warming up (503) or failed, return gracefully
        if user_vector is None or not isinstance(user_vector, list):
            return jsonify({"message": "AI model is warming up or busy. Please try a shorter search or wait 15 seconds."}), 503
            
        try:
            # --- FIX: Shape Handling Matrix Normalization ---
            user_vector_np = np.array(user_vector)

            # Force the shape to (1, 384) regardless of what the API spits out
            if user_vector_np.ndim == 1:
                user_vector_np = user_vector_np.reshape(1, -1)
            elif user_vector_np.ndim == 2:
                # If it's (sequence_length, 384), mean pool it to avoid 3D array errors down the line
                if user_vector_np.shape[0] > 1:
                    user_vector_np = np.mean(user_vector_np, axis=0).reshape(1, -1)

            # Safely calculate similarity now that dimensions are strictly controlled
            similarities = cosine_similarity(user_vector_np, book_embeddings)[0]
            top_indices = np.argsort(similarities)[-10:][::-1]
            recommended_ids = [book_ids[i] for i in top_indices]
            books = Book.query.filter(Book.book_id.in_(recommended_ids)).all()
            
        except Exception as e:
            print(f"Search Vector Error: {str(e)}")
            return jsonify({"message": "An error occurred during semantic search parsing."}), 500
    else:
        # Fallback to lightning-fast relational database lookup for short keyword strings
        books = book_query.filter((Book.title.contains(query_text)) | (Book.authors.contains(query_text))).limit(20).all()

    return jsonify([{
        "book_id": b.book_id, "title": b.title, "authors": b.authors,
        "genres": b.genres, "average_rating": b.average_rating, "image_url": b.image_url
    } for b in books])

@app.route('/api/admin/rebuild_embeddings', methods=['POST'])
def rebuild_embeddings():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"message": "Unauthorized"}), 401

    def generate():
        try:
            books = Book.query.filter(Book.description.isnot(None)).all()
            if not books: return
            
            new_book_ids, combined_texts = [], []
            for book in books:
                new_book_ids.append(book.book_id)
                combined_texts.append(f"Genre: {book.genres}. Description: {book.description}")

            yield f"data: {json.dumps({'progress': 20, 'message': 'Sending to HF API...'})}\n\n"
            
            # Note: For very large datasets, you should chunk combined_texts 
            # because the API has a limit on input size per request.
            new_embeddings = query_hf_api(combined_texts)
            
            with open("book_embeddings.pkl", "wb") as f:
                pickle.dump({"book_ids": new_book_ids, "embeddings": new_embeddings}, f)

            global book_ids, book_embeddings
            book_ids, book_embeddings = new_book_ids, new_embeddings
            yield f"data: {json.dumps({'progress': 100, 'message': 'Cloud Brain Updated!'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'progress': 0, 'message': f'Error: {str(e)}'})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

# --- REMAINING BOILERPLATE ROUTES ---
@app.route('/bookmarks_page')
def bookmarks_page():
    if 'user_id' not in session: return redirect('/login_page')
    user_bookmarks = Bookmark.query.filter_by(user_id=session['user_id']).order_by(Bookmark.saved_at.desc()).all()
    return render_template('bookmarks.html', books=user_bookmarks)

@app.route('/api/bookmark/<int:book_id>', methods=['POST'])
def add_bookmark(book_id):
    if 'user_id' not in session: return jsonify({"message": "Login required"}), 401
    if not Bookmark.query.filter_by(user_id=session['user_id'], book_id=book_id).first():
        db.session.add(Bookmark(user_id=session['user_id'], book_id=book_id))
        db.session.commit()
    return jsonify({"message": "Success"}), 200

@app.route('/api/bookmark/remove/<int:book_id>', methods=['DELETE'])
def remove_bookmark(book_id):
    if 'user_id' not in session:
        return jsonify({"message": "Login required"}), 401
    
    # Find the specific bookmark for this user and this book
    bookmark = Bookmark.query.filter_by(
        user_id=session['user_id'], 
        book_id=book_id
    ).first()

    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({"message": "Bookmark removed"}), 200
    
    return jsonify({"message": "Bookmark not found"}), 404

@app.route('/searchbook_page')
def searchbook_page():
    is_logged_in = 'user_id' in session
    user_name = User.query.get(session['user_id']).name if is_logged_in else "Guest"
    return render_template('search.html', user_name=user_name, is_logged_in=is_logged_in)

@app.route('/profile_page')
def profile_page():
    if 'user_id' not in session: return redirect('/login_page')
    return render_template('profile.html', user=User.query.get(session['user_id']))

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401
    
    data = request.get_json()
    user = User.query.get(session['user_id'])
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Update Name and Email
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)

    # Update Password only if a new one is provided
    new_password = data.get('password')
    if new_password and new_password.strip() != "":
        user.set_password(new_password) # This hashes the password automatically

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Email might already be in use."}), 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login_page')

@app.route('/result_page')
def result_page():
    return render_template('result.html')

@app.route('/api/save_genre', methods=['POST'])
def save_genre():
    if 'user_id' not in session: return jsonify({"message": "Guest"}), 200
    user = User.query.get(session['user_id'])
    user.current_genre = request.get_json().get('genre')
    db.session.commit()
    return jsonify({"message": "Updated"}), 200

@app.route('/details/<int:book_id>')
def details_page(book_id):
    book = Book.query.get_or_404(book_id)
    is_bookmarked = False
    if 'user_id' in session:
        is_bookmarked = Bookmark.query.filter_by(user_id=session['user_id'], book_id=book_id).first() is not None
    return render_template('details.html', book=book, is_bookmarked=is_bookmarked)

@app.route('/login_page')
def login_page(): return render_template('login.html')

@app.route('/signup_page')
def signup_page(): return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    password = data.get('password', '')

    # Regex breakdown:
    # (?=.*[a-zA-Z]) : Must contain at least one letter
    # (?=.*\d)       : Must contain at least one number
    # (?=.*[@$!%*?&]): Must contain at least one symbol
    # .{8,}          : Must be at least 8 characters long
    password_regex = r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
    
    if not re.match(password_regex, password):
        return jsonify({
            "message": "Password must be at least 8 characters and include a letter, a number, and a symbol (@$!%*?&)."
        }), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first(): 
        return jsonify({"message": "Email already exists"}), 400
        
    u = User(name=data['name'], email=data['email'])
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return jsonify({"message": "Account created!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    u = User.query.filter_by(email=data['email']).first()
    if u and u.check_password(data['password']):
        if u.email == 'michael@admin.com': 
            u.role = 'admin'
            db.session.commit()
        session['user_id'], session['role'] = u.user_id, u.role
        
        # FIX: Added the "message" key to the dictionary
        return jsonify({
            "message": "Login successful! Redirecting...", 
            "redirect": "/admin_dashboard" if u.role == 'admin' else "/"
        }), 200
        
    return jsonify({"message": "Invalid email or password"}), 401

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect('/login_page')
    total_books, total_users = Book.query.count(), User.query.count()
    page = request.args.get('page', 1, type=int)
    pagination = Book.query.order_by(Book.book_id.desc()).paginate(page=page, per_page=50)
    return render_template('admin.html', books=pagination.items, pagination=pagination, total_books=total_books, total_users=total_users)

# --- ADMIN USER MANAGEMENT ROUTES ---

@app.route('/admin_users')
def admin_users():
    """Renders the dashboard displaying all registered users."""
    if session.get('role') != 'admin': 
        return redirect('/login_page')
    
    # Fetch all users to display in management window
    users = User.query.order_by(User.user_id.desc()).all()
    return render_template('admin_users.html', users=users)


@app.route('/api/admin/user/delete/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    """Allows administrators to drop users out of the system cleanly."""
    if session.get('role') != 'admin':
        return jsonify({"message": "Unauthorized"}), 401
    
    # Don't let an admin accidentally delete their own active session profile
    if session.get('user_id') == user_id:
        return jsonify({"message": "You cannot delete your own admin account while active."}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User entity not found."}), 404

    try:
        # Cascade-delete bookmarks associated with user first to protect foreign key constraint
        Bookmark.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500


@app.route('/api/admin/user/save', methods=['POST'])
def admin_save_user():
    """Updates an existing user's name, email, or credential hash explicitly."""
    if session.get('role') != 'admin':
        return jsonify({"message": "Unauthorized"}), 401
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"message": "Missing user identifier."}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404

    # Email collision logic check
    new_email = data.get('email')
    if new_email and new_email != user.email:
        existing = User.query.filter_by(email=new_email).first()
        if existing:
            return jsonify({"message": "Email is already assigned to a different account."}), 400
        user.email = new_email

    # Update basic profile info
    user.name = data.get('name', user.name)
    
    # Manage explicit changes to password string safely
    password = data.get('password')
    if password and password.strip() != "":
        user.set_password(password)

    try:
        db.session.commit()
        return jsonify({"message": "User profile successfully modified."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)