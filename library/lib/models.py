from django.db import models
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError

N_SHELF = 5
N_SHELF_SLOT = 6
N_BOOK_SLOT = 10

# За каждым залом закреплен библиотекарь.
class Librarian(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

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

    librarian = models.OneToOneField(Librarian, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Hall {self.id}, librarian is {self.librarian}"

# Каждый стеллаж имеет уникальный номер в рамках зала. В каждом зале установлено 5 стеллажей.
class Shelf(models.Model):

    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    number = models.PositiveIntegerField(validators=[MaxValueValidator(N_SHELF)])

    def __str__(self):
        return f"Shelf {self.number} in Hall {self.hall.id}"

class ShelfSlot(models.Model):

    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE)
    # На каждом стеллаже есть 6 полок. 
    slot_number = models.IntegerField(validators=[MaxValueValidator(N_SHELF_SLOT)])
    books = models.ManyToManyField(Book, through='BookShelf', blank=True)

    def __str__(self):
        return f'ShelfSlot {self.slot_number} on {self.shelf}'

class BookShelf(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    shelf_slot = models.ForeignKey(ShelfSlot, on_delete=models.CASCADE)

    def clean(self):
            super().clean()

            current_books_count = BookShelf.objects.filter(shelf_slot=self.shelf_slot).count()

            if current_books_count >= N_BOOK_SLOT:
                raise ValidationError(f"На полке не может быть более {N_BOOK_SLOT} книг")

class Reader(models.Model):

    name = models.CharField(max_length=255)
    borrowed_books = models.ManyToManyField(Book, through='Borrow')

class Borrow(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    return_date = models.DateField()
    return_date_fact = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)

# При этом книги периодически перемещаются между залами, стеллажами и полками.
# За каждым залом закреплен библиотекарь. Все перемещения книг библиотекари отмечают в специальном журнале.
class BookMovement(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    from_shelf_slot = models.ForeignKey(ShelfSlot, on_delete=models.CASCADE, related_name='from_shelf_slot')
    to_shelf_slot = models.ForeignKey(ShelfSlot, on_delete=models.CASCADE, related_name='to_shelf_slot')
    date = models.DateField()