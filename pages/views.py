from django.http import JsonResponse
from django.db.models import Min, Max, Count, Avg
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Book, Review
from .serializers import UserRegisterSerializer, BookSerializer, ReviewSerializer


def api_home(request):
    return JsonResponse({
        "message": "Welcome to the Book Metadata API",
        "available_endpoints": [
            "/register/",
            "/login/",
            "/books/",
            "/books/stats/",
            "/books/recent/",
            "/books/categories/",
            "/reviews/",
            "/reviews/<id>/",
            "/books/<id>/",
            "/admin/"
        ]
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "message": "User registered successfully"
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def book_list(request):
    if request.method == 'GET':
        books = Book.objects.all()

        title = request.GET.get('title')
        author = request.GET.get('author')
        year = request.GET.get('year')
        category = request.GET.get('category')
        ordering = request.GET.get('ordering')

        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1

        try:
            page_size = int(request.GET.get('page_size', 20))
        except ValueError:
            page_size = 20

        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100

        if title:
            books = books.filter(title__icontains=title)
        if author:
            books = books.filter(author__icontains=author)
        if year:
            books = books.filter(published_year=year)
        if category:
            books = books.filter(category__icontains=category)

        allowed_ordering = ['title', '-title', 'published_year', '-published_year']
        if ordering in allowed_ordering:
            books = books.order_by(ordering)

        total_count = books.count()
        start = (page - 1) * page_size
        end = start + page_size
        books = books[start:end]

        serializer = BookSerializer(books, many=True)
        return Response({
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "results": serializer.data
        })

    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def book_stats(request):
    total_books = Book.objects.count()
    books_with_description = Book.objects.exclude(description="").count()
    oldest_year = Book.objects.aggregate(Min('published_year'))['published_year__min']
    newest_year = Book.objects.aggregate(Max('published_year'))['published_year__max']
    unique_categories = Book.objects.exclude(category="").values('category').distinct().count()

    return Response({
        "total_books": total_books,
        "books_with_description": books_with_description,
        "oldest_year": oldest_year,
        "newest_year": newest_year,
        "unique_categories": unique_categories
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def recent_books(request):
    books = Book.objects.exclude(published_year__isnull=True).order_by('-published_year')[:10]
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def category_summary(request):
    categories = (
        Book.objects.exclude(category="")
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    return Response(list(categories))


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def book_detail(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_list(request):
    if request.method == 'GET':
        reviews = Review.objects.all()
        book_id = request.GET.get('book')

        if book_id:
            reviews = reviews.filter(book_id=book_id)

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required to create a review"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def review_detail(request, pk):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if review.user != request.user:
            return Response(
                {"error": "You can only edit your own review"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReviewSerializer(review, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if review.user != request.user:
            return Response(
                {"error": "You can only delete your own review"},
                status=status.HTTP_403_FORBIDDEN
            )

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def top_rated_books(request):
    books = (
        Book.objects.annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
        .filter(review_count__gt=0)
        .order_by('-average_rating', '-review_count')[:10]
    )

    data = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "average_rating": round(book.average_rating, 2) if book.average_rating is not None else None,
            "review_count": book.review_count,
        }
        for book in books
    ]
    return Response(data)