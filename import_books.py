import pandas as pd
from app import app, db, Book

# 1. Load the Excel file
file_path = r"C:\Users\Michael Lian\Desktop\FYP 2\Recobook_Project\recobook_english_only2.xlsx"
df = pd.read_excel(file_path)

# 2. Select the columns including your 2 new additions
# Ensure 'average_rating' and 'image_url' match the exact column names in your Excel file
df = df[['original_title', 'authors', 'genres', 'description', 'image_url', 'average_rating']]

with app.app_context():
    print("Starting fresh import... resetting database table.")
    # Optional: Clear existing books to avoid duplicates during a reset
    # db.session.query(Book).delete() 
    
    for index, row in df.iterrows():
        # Create a new Book object with the updated schema
        new_book = Book(
            title=str(row['original_title']),
            authors=str(row['authors']),
            genres=str(row['genres']),
            description=str(row['description']),
            image_url=str(row['image_url']),      # New Column
            average_rating=float(row['average_rating']) # New Column
        )
        db.session.add(new_book)
        
        # Commit every 500 books to keep it fast
        if index % 500 == 0:
            db.session.commit()
            print(f"Imported {index} books...")

    db.session.commit()
    print(f"Success! {len(df)} books with ratings and images are now in your database.")