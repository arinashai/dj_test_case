from django.db import models
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError

# За каждым залом закреплен библиотекарь.
class Librarian(models.Model):
    name = models.CharField(max_length=100)

# Для каждой книги заведена карточка, в которой отражаются: 
# название книги, автор, вид издания, номер,
# количество страниц, дата издания, описание

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    edition_type = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    page_count = models.PositiveIntegerField()
    publication_date = models.PositiveIntegerField()
    description = models.TextField()

    def __str__(self):
        return self.title

# Поскольку книг много - их хранят в различных залах библиотеки.
class Hall(models.Model):

    librarian = models.ForeignKey(Librarian, on_delete=models.SET_NULL, null=True)
    # стеллажи в рамках зала
    shelves = models.ManyToManyField('Shelf', related_name='hall_shelves')

    def __str__(self):
        return f"Hall {self.id}, librarian is {self.librarian}"

# Каждый стеллаж имеет уникальный номер в рамках зала. В каждом зале установлено 5 стеллажей.
class Shelf(models.Model):
    number = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)