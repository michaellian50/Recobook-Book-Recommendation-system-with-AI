import sqlite3
import pickle
import numpy as np
import requests
import time

# --- CONFIGURATION ---
# We go back to the /models/ endpoint but with a more robust request
HF_API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
HF_TOKEN = "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" 
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
    "X-Wait-For-Model": "true" # Forces the API to load the model if it's sleeping
}


def query_hf_api(texts):
    payload = {
        "inputs": texts,
        "options": {
            "wait_for_model": True,
            "use_cache": False
        }
    }

    max_retries = 6

    for attempt in range(max_retries):
        try:
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json=payload,
                timeout=180
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                return response.json()

            elif response.status_code in [503, 404]:
                print(f"Model loading... waiting 60s ({attempt+1}/{max_retries})")
                time.sleep(60)

            elif response.status_code == 429:
                print("Rate limited. Waiting 90s...")
                time.sleep(90)

            else:
                print("ERROR RESPONSE:")
                print(response.text)
                return None

        except Exception as e:
            print(f"Connection Error: {e}")
            time.sleep(30)

    return None

# 1. Connect to Database
conn = sqlite3.connect('instance/recobook.db')
cursor = conn.cursor()

# 2. Pull Data
cursor.execute("SELECT book_id, genres, description FROM book WHERE description IS NOT NULL")
books = cursor.fetchall() 

book_ids = []
combined_texts = []

for b_id, genre, desc in books:
    book_ids.append(b_id)
    genre_text = genre if genre else "Unknown"
    # Keep your weighted logic
    combined_texts.append(f"Genre: {genre_text}. {genre_text}. Description: {desc}")

print(f"Starting vectorization for {len(combined_texts)} books...")

# 3. Process in Chunks
all_embeddings = []
chunk_size = 50 # 50 is the 'sweet spot' for free tier payload limits

for i in range(0, len(combined_texts), chunk_size):
    chunk = combined_texts[i:i + chunk_size]
    print(f"Processing chunk {i//chunk_size + 1} ({i} to {min(i + chunk_size, len(combined_texts))})...")
    
    result = query_hf_api(chunk)
    
    if result and isinstance(result, list):
        all_embeddings.extend(result)
    else:
        print(f"Failed at chunk starting at index {i}. Check your terminal logs above.")
        break
    
    # Increase to 3 seconds to avoid '429 Too Many Requests' during long runs
    time.sleep(3)

# 4. Save results
if len(all_embeddings) == len(book_ids):
    embeddings_np = np.array(all_embeddings)
    
    # Flatten if API returned 3D
    if len(embeddings_np.shape) == 3:
        embeddings_np = embeddings_np.reshape(len(book_ids), -1)

    with open("book_embeddings.pkl", "wb") as f:
        pickle.dump({"book_ids": book_ids, "embeddings": embeddings_np}, f)

    print(f"Success! Generated {len(all_embeddings)} vectors.")
else:
    print(f"Mismatch: Got {len(all_embeddings)} embeddings for {len(book_ids)} books.")

conn.close()