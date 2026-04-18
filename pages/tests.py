from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import Book


class BookAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.book1 = Book.objects.create(
            title="Python Basics",
            author="John Smith",
            published_year=2020,
            category="Programming",
            description="An introduction to Python."
        )

        self.book2 = Book.objects.create(
            title="Advanced Django",
            author="Jane Doe",
            published_year=2022,
            category="Web Development",
            description="Deep dive into Django."
        )

    def test_api_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.json())

    def test_get_books_list(self):
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["total_count"], 2)

    def test_get_single_book(self):
        response = self.client.get(f'/books/{self.book1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Python Basics")

    def test_book_not_found(self):
        response = self.client.get('/books/999999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_book(self):
        data = {
            "title": "Data Science 101",
            "author": "Alice Brown",
            "published_year": 2021,
            "category": "Data Science",
            "description": "Basic concepts of data science."
        }
        response = self.client.post('/books/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)

    def test_search_books_by_title(self):
        response = self.client.get('/books/?title=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 1)

    def test_filter_books_by_category(self):
        response = self.client.get('/books/?category=Programming')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_count"], 1)

    def test_order_books_by_year_desc(self):
        response = self.client.get('/books/?ordering=-published_year')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Advanced Django")

    def test_pagination(self):
        response = self.client.get('/books/?page=1&page_size=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["total_count"], 2)

    def test_get_book_stats(self):
        response = self.client.get('/books/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_books"], 2)

    def test_get_recent_books(self):
        response = self.client.get('/books/recent/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_category_summary(self):
        response = self.client.get('/books/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))