from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=150, blank=True)
    published_year = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author", "published_year"],
                name="unique_book_record"
            )
        ]

    def __str__(self):
        return self.title