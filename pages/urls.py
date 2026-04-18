from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    api_home,
    register_user,
    book_list,
    book_detail,
    book_stats,
    recent_books,
    category_summary,
    review_list,
    review_detail,
    top_rated_books,
)

urlpatterns = [
    path('', api_home, name='api-home'),

    path('register/', register_user, name='register-user'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('books/', book_list, name='book-list'),
    path('books/stats/', book_stats, name='book-stats'),
    path('books/recent/', recent_books, name='recent-books'),
    path('books/categories/', category_summary, name='category-summary'),
    path('books/top-rated/', top_rated_books, name='top-rated-books'),
    path('books/<int:pk>/', book_detail, name='book-detail'),

    path('reviews/', review_list, name='review-list'),
    path('reviews/<int:pk>/', review_detail, name='review-detail'),
]
