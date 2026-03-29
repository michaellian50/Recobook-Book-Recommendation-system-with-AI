# Recobook: AI-Powered Book Recommendation System

Recobook is an intelligent book discovery platform built for my Final Year Project (FYP) at Universiti Malaysia Sarawak (UNIMAS). It leverages Natural Language Processing (NLP) to match users with books based on their moods, preferences, and open-ended descriptions.

## Key Features

* **Semantic Discovery Quiz:** A 5-step hybrid quiz that "stitches" user answers into a rich preference profile.
* **AI Recommendation Engine:** Powered by the `all-MiniLM-L6-v2` Sentence-Transformer model.
* **Hybrid Search:** Supports both keyword-based searching (Title/Author) and semantic "mood" searching.
* **Personalized Bookmarks:** Users can save books to their profile with automated "Saved Date" tracking.
* **Admin Dashboard:** Full CRUD (Create, Read, Update, Delete) capabilities for managing the book database.
* **Secure Authentication:** User registration and login with hashed passwords via `Werkzeug`.

## Tech Stack

* **Backend:** Python 3.x, Flask
* **Database:** SQLite with SQLAlchemy ORM
* **AI/ML:** Sentence-Transformers (all-MiniLM-L6-v2), Scikit-Learn (Cosine Similarity), NumPy
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/recobook.git](https://github.com/yourusername/recobook.git)
   cd recobook
2. **Install dependencies**
   Make sure you have pip installed.
   ```bash
   pip install -r requirements.txt
3. **Initialize the Database**
    The database recobook.db will be automatically created when you run the app for the first time.
    ```bash
    python app.py
4. **Access the Application**
   Open your browser and navigate to:
   http://127.0.0.1:5000

👤 Author
Michael Lian
Computer Science (Multimedia Computing) Student
Universiti Malaysia Sarawak (UNIMAS)

This project was developed for academic purposes at UNIMAS.
