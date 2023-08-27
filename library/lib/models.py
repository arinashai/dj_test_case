from django.db import models

# Для каждой книги заведена карточка, в которой отражаются: 
# название книги, автор, вид издания, номер,
# количество страниц, дата издания, описание

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    edition = models.CharField(max_length=50)
    number = models.PositiveIntegerField()
    page_count = models.PositiveIntegerField()
    publication_date = models.DateField()
    description = models.TextField()

#    def __str__(self):
#        return self.title

# Поскольку книг много - их хранят в различных залах библиотеки.
# За каждым залом закреплен библиотекарь.
#class Hall(models.Model):
