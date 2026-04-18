from django.urls import path
from .views import api_home, book_list, book_detail, book_stats, recent_books, category_summary

urlpatterns = [
    path('', api_home, name='api-home'),
    path('books/', book_list, name='book-list'),
    path('books/stats/', book_stats, name='book-stats'),
    path('books/recent/', recent_books, name='recent-books'),
    path('books/categories/', category_summary, name='category-summary'),
    path('books/<int:pk>/', book_detail, name='book-detail'),
]