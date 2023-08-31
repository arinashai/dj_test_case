from datetime import timedelta
from django.utils import timezone
from lib.models import Borrow, Hall, BookShelf, Book

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
    BookShelf.objects.filter(book=book).update(book=None)

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

# Для удобства поиска библиотекари иногда переставляют все книги, 
# чтобы получилась следующая сортировка:
# по виду издания, названию, году издания 
# и количеству страниц в порядке возрастания.

def sorting_books():
    sorted_books = Book.objects.all().order_by(
        'edition_type', 'title', 'publication_date', 'page_count'
    )

    bookshelves = BookShelf.objects.all().order_by(
        'shelfslot__shelf__hall', 'shelfslot__shelf__number', 'shelfslot__slot_number'
    )

    # Связываем отсортированные книги с соответствующими слотами на полках
    for bookshelf, book in zip(bookshelves, sorted_books):
        bookshelf.book = book
        bookshelf.save()

    # Очищаем оставшиеся слоты на полках, если книг меньше, чем слотов
    for bookshelf in BookShelf.objects.filter(id > sorted_books.count()):
        bookshelf.book = None
        bookshelf.save()

# Периодически библиотекарям требуется сборка следующих отчетов:
#- Количество книг определенного автора в библиотеке
#- 10 самых популярных книг за последний месяц
#- Количество книг, которые сейчас находятся на руках в разрезе читателей - Перечень читателей, которые просрочили возврат книг
#- 10 самых активных читателей, которые взяли больше всего книг, за прошедший месяц - Среднее количество страниц в разрезе видов изданий, которые прочитали читатели за последний месяц
#- 10 самых перемещаемых книг за последний месяц