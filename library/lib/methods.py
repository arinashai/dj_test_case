from datetime import timedelta, datetime
from django.utils import timezone
from lib.models import Borrow, Hall, BookShelf, Book, BookMovement, ShelfSlot
from django.db.models import Count, Avg

MAX_READER_BOOK = 3
RETURN_DEADLINE_DAYS = 30

class FoundEmptySlot(Exception):
    pass

class EmptySlotNotFound(Exception):
    pass

def last_month_date():
    return datetime.now() - timedelta(days=30)

def bookmovement(book, to_slot):
    date = datetime.now()
    from_slot = ShelfSlot.objects.get(books=book)
    # Перемещаем
    BookShelf.objects.filter(book=book).update(shelf_slot=to_slot)
    # Записываем перемещения
    move = BookMovement(book=book, from_shelf_slot=from_slot, to_shelf_slot=to_slot, date=date)
    move.save()
    return 'Перемещения книги внесены в журнал.'

def borrowing_book(reader, book):

    # Книгу уже взял другой читатель и ее нет в наличии
    if Borrow.objects.filter(book=book, returned=False).exists():
        return 'Книги нет в наличии.'

    # Читатель уже взял и держит у себя 3 книги, поэтому больше взять не может, пока не вернет их
    if Borrow.objects.filter(reader=reader, returned=False).count()>=MAX_READER_BOOK:
        return f'Читатель уже взял максимальное количество книг: {MAX_READER_BOOK}.'
    
    borrow_date = timezone.now()

    # Каждая книга может быть взята на срок не более 30 дней.
    return_date = borrow_date + timedelta(days=RETURN_DEADLINE_DAYS) 

    # Убираем книгу с полки
    BookShelf.objects.filter(book=book).update(book=None)

    Borrow.objects.create(book=book, reader=reader, borrow_date=borrow_date, return_date=return_date)
    return 'Книга успешно взята.'

def returning_book(reader, book):

    if not Borrow.objects.filter(reader=reader, book=book):
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

        Borrow.objects.filter(reader=reader, book=book).update(returned=True)
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
        'shelf_slot__shelf__hall', 'shelf_slot__shelf__number', 'shelf_slot__slot_number'
    )

    # Связываем отсортированные книги с соответствующими слотами на полках
    for bookshelf, book in zip(bookshelves, sorted_books):
        bookshelf.book = book
        bookshelf.save()

    # Очищаем оставшиеся слоты на полках, если книг меньше, чем слотов
    for bookshelf in BookShelf.objects.filter(id__gt=sorted_books.count()):
        bookshelf.book = None
        bookshelf.save()
    return 'Книги отсортированы.'

# Количество книг определенного автора в библиотеке
def books_by_author(author):
    return Book.objects.filter(author=author).count()

# 10 самых популярных книг за последний месяц (30 дней?)
def top_10_books():
    last_month = last_month_date() 
    return Borrow.objects.filter(borrow_date__gte=last_month).values('book__title').annotate(count=Count('book')).order_by('-count')[:10]

# Количество книг, которые сейчас находятся на руках в разрезе читателей
def books_borrowed_by_readers():
    return Borrow.objects.filter(returned=False).values('reader__name').annotate(count=Count('book'))

# Перечень читателей, которые просрочили возврат книг
def readers_delay():
    return Borrow.objects.filter(return_date__gt=datetime.now(), returned=False).values('reader')

# 10 самых активных читателей, которые взяли больше всего книг, за прошедший месяц
def top_10_active_readers():
    last_month = last_month_date() 
    return Borrow.objects.filter(borrow_date__gte=last_month).values('reader__name').annotate(count=Count('book')).order_by('-count')[:10]

# Среднее количество страниц в разрезе видов изданий, которые прочитали читатели за последний месяц
def read_avg_page_count():
    last_month = last_month_date() 
    return Borrow.objects.filter(borrow_date__gte=last_month).values('book__edition_type').annotate(average_pages=Avg('book__page_count'))

# 10 самых перемещаемых книг за последний месяц
def top_10_bookmovements():
    last_month = last_month_date()
    return BookMovement.objects.filter(date__gte = last_month).values('book__title').annotate(count=Count('book')).order_by('-count')[:10]