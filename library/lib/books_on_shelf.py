from lib.models import Book, ShelfSlot, BookShelf
import random
from django.db import transaction

# Заполнение стелажей и полок

n_books_per_slot = 10

books = Book.objects.all()
shelf_slots = ShelfSlot.objects.all()

with transaction.atomic():
    for shelf_slot in shelf_slots:
        available_books = list(books)  # Создаем копию списка книг
        random.shuffle(available_books)  # Перемешиваем книги случайным образом

        for _ in range(n_books_per_slot):
            if available_books:
                book = available_books.pop()
                BookShelf.objects.create(book=book, shelf_slot=shelf_slot)
            else:
                break  # Выход, если книги закончились

