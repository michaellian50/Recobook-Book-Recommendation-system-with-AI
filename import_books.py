import pandas as pd
from app import app, db, Book

# 1. Load the Excel file
file_path = r"C:\Users\Michael Lian\Desktop\FYP 2\Recobook_Project\recobook_english_only.xlsx"
df = pd.read_excel(file_path)

# 2. Select only the columns we need
df = df[['original_title', 'authors', 'genres', 'description', 'image_url']]

with app.app_context():
    print("Starting import... this may take a minute.")
    for index, row in df.iterrows():
        # Create a new Book object
        new_book = Book(
            title=str(row['original_title']),
            authors=str(row['authors']),
            genres=str(row['genres']),
            description=str(row['description']),
        )
        db.session.add(new_book)
        
        # Commit every 500 books to keep it fast
        if index % 500 == 0:
            db.session.commit()
            print(f"Imported {index} books...")

    db.session.commit()
    print("Success! 10,000 books are now in your database.")