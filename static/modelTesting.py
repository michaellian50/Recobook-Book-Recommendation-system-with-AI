from sentence_transformers import SentenceTransformer, util

# 1. Load the model (It will download to your local cache the first time)
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Your Book Database (In FYP 2, this will come from your SQL/NoSQL DB)
books = [
    {"title": "The Hobbit", "desc": "A fantasy adventure with dragons, magic, and a quest for treasure."},
    {"title": "Murder on the Orient Express", "desc": "A classic detective mystery involving a closed-room crime on a train."},
    {"title": "The Silent Patient", "desc": "A psychological thriller about a woman's act of violence against her husband."},
    {"title": "Atomic Habits", "desc": "A self-help guide on building good habits and breaking bad ones."},
    {"title": "Dune", "desc": "An epic sci-fi saga about politics, religion, and survival on a desert planet."}
]

# 3. Simulate Quiz Results
# Instead of "I like Sci-Fi", the quiz might produce a "Profile String" like this:
user_quiz_profile = "I enjoy stories about solving crimes, dark secrets, and intense suspense."

# 4. The Matching Logic
# Step A: Encode the book descriptions
book_descriptions = [b['desc'] for b in books]
book_embeddings = model.encode(book_descriptions)

# Step B: Encode the user profile
user_embedding = model.encode(user_quiz_profile)

# Step C: Compute Cosine Similarity (The Mathematical Match)
cosine_scores = util.cos_sim(user_embedding, book_embeddings)[0]

# 5. Display Results
print(f"User Interest: '{user_quiz_profile}'\n")
print("--- Recommendations ---")

# Match scores to titles and sort them
results = []
for i in range(len(books)):
    results.append({'title': books[i]['title'], 'score': cosine_scores[i].item()})

# Sort by highest score
results = sorted(results, key=lambda x: x['score'], reverse=True)

for res in results:
    print(f"Book: {res['title']:<30} | Match Score: {res['score']:.4f}")