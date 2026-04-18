import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookproject.settings")
django.setup()

from pages.models import Book

books = pd.read_csv("books_sample.csv")

count = 0

for _, row in books.iterrows():
    Book.objects.update_or_create(
        title=row["title"] if pd.notna(row["title"]) else "",
        author=row["author"] if pd.notna(row["author"]) else "",
        published_year=int(row["published_year"]) if pd.notna(row["published_year"]) else None,
        defaults={
            "category": row["category"] if pd.notna(row["category"]) else "",
            "description": row["description"] if pd.notna(row["description"]) else "",
        }
    )
    count += 1

print(f"Imported {count} books into database.")