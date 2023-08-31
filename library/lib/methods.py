from datetime import timedelta
from django.utils import timezone
from lib.models import Borrow, Hall, BookShelf
from django.db.models import Value

MAX_READER_BOOK = 3
RETURN_DEADLINE_DAYS = 30

class FoundEmptySlot(Exception):
    pass

class EmptySlotNotFound(Exception):
    pass

def borrowing_book(reader, book):
    # Книгу уже взял другой читатель и ее нет в наличии
    if Borrow.objects.filter(book=book, returned=False).exists():
        return 'Книги нет в наличии.'
    # Читатель уже взял и держит у себя 3 книги, поэтому больше взять не может, пока не вернет их
    if Borrow.objects.filter(reader=reader, returned=False) > 2:
        return f'Читатель уже взял максимальное количество книг: {MAX_READER_BOOK}.'
    
    borrow_date = timezone.now()
    # Каждая книга может быть взята на срок не более 30 дней.
    return_date = borrow_date + timedelta(days=RETURN_DEADLINE_DAYS) 

    # Убираем книгу с полки
    BookShelf.objects.filter(book=book).update(book=Value(None))

    Borrow.objects.create(book=book, reader=reader, borrow_date=borrow_date, return_date=return_date)
    return 'Книга успешно взята.'

def returning_book(reader, book):

    if Borrow.objects.filter(reader=reader, book=book).exists():
        return 'Читатель не может вернуть книгу, которую не брал.'
    if Borrow.objects.filter(reader=reader, book=book,  returned=True).exists():
        return 'Читатель уже вернул книгу.'

    halls = Hall.objects.all()

    # Размещаем книгу в первый свободный зал, 
    # на первый свободный стеллаж, на первую свободную полку. 
    try:
        for hall in halls:
            shelves = hall.shelf_set.all()

            for shelf in shelves:
                shelf_slots = shelf.shelfslot_set.all()
        
                empty_slot = shelf_slots.filter(bookshelf__book__isnull=True).first()
                if empty_slot:
                    empty_slot.bookshelf_set.update(book=book)
                    raise FoundEmptySlot
        raise EmptySlotNotFound

    except FoundEmptySlot:

        return_date_fact = timezone.now()
        Borrow.objects.filter(reader=reader, book=book).update(return_date_fact=return_date_fact, returned=True)
        return 'Книга успешно возвращена.'

    except EmptySlotNotFound:
        return 'Все полки заняты.'