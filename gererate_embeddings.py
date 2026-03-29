import sqlite3
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load the AI Model
print("Loading AI Model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Connect to your Recobook Database
conn = sqlite3.connect('instance/recobook.db')
cursor = conn.cursor()

# 3. Pull all books that have a description
cursor.execute("SELECT book_id, description FROM book WHERE description IS NOT NULL")
books = cursor.fetchall() # This gives us a list of (id, description)

book_ids = [b[0] for b in books]
descriptions = [b[1] for b in books]

print(f"Vectorizing {len(descriptions)} book descriptions. Please wait...")

# 4. The AI Magic: Turn text into numbers (Vectors)
# show_progress_bar=True helps you see how long it takes
embeddings = model.encode(descriptions, show_progress_bar=True)

# 5. Save the results so we never have to do this again
data_to_save = {
    "book_ids": book_ids,
    "embeddings": embeddings
}

with open("book_embeddings.pkl", "wb") as f:
    pickle.dump(data_to_save, f)

print("Success! 'book_embeddings.pkl' has been created.")
conn.close()