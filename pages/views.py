from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.db.models import Min, Max, Count
from django.db.models import Count

from .models import Book
from .serializers import BookSerializer


def api_home(request):
    return JsonResponse({
        "message": "Welcome to the Book Metadata API",
        "available_endpoints": [
            "/books/",
            "/books/stats/",
            "/books/<id>/",
            "/admin/"
        ]
    })


@api_view(['GET', 'POST'])
def book_list(request):
    if request.method == 'GET':
        books = Book.objects.all()

        title = request.GET.get('title')
        author = request.GET.get('author')
        year = request.GET.get('year')
        category = request.GET.get('category')
        ordering = request.GET.get('ordering')

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

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
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
def recent_books(request):
    books = Book.objects.exclude(published_year__isnull=True).order_by('-published_year')[:10]
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_summary(request):
    categories = (
        Book.objects.exclude(category="")
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    return Response(list(categories))

@api_view(['GET', 'PUT', 'DELETE'])
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