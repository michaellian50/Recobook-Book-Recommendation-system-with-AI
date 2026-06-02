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

# 3. Pull book_id, genre, and description
# Note: I'm selecting 'genre' now as well.
cursor.execute("SELECT book_id, genres, description FROM book WHERE description IS NOT NULL")
books = cursor.fetchall() 

book_ids = []
combined_texts = []

for b_id, genre, desc in books:
    book_ids.append(b_id)
    
    # Handle potential None values for genre
    genre_text = genre if genre else "Unknown Genre"
    
    # COMBINING LOGIC: 
    # We put the genre at the front and repeat it slightly to give it more 'weight'
    # Final format: "Genre: Fantasy. Fantasy. Description: A story about..."
    text_to_vectorize = f"Genre: {genre_text}. {genre_text}. Description: {desc}"
    combined_texts.append(text_to_vectorize)

print(f"Vectorizing {len(combined_texts)} books (Genre + Description). Please wait...")

# 4. The AI Magic: Turn the combined text into Vectors
embeddings = model.encode(combined_texts, show_progress_bar=True)

# 5. Save the results
data_to_save = {
    "book_ids": book_ids,
    "embeddings": embeddings
}

with open("book_embeddings.pkl", "wb") as f:
    pickle.dump(data_to_save, f)

print("Success! 'book_embeddings.pkl' has been updated with Genre + Description data.")
conn.close()