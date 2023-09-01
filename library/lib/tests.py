from django.test import TestCase
from lib.models import Book, Reader, Librarian, Hall, Shelf, ShelfSlot
from lib.models import Borrow, BookShelf, BookMovement
from lib.methods import borrowing_book, MAX_READER_BOOK
from lib.methods import returning_book, sorting_books, bookmovement
from lib.models import N_SHELF, N_SHELF_SLOT, N_BOOK_SLOT

class BorrowingBookTestCase(TestCase):

    def setUp(self):
        self.reader = Reader.objects.create(name='Test reader')
        self.book = Book.objects.create(title='Test book', 
                                        page_count=100, 
                                        publication_date=2023)

    def test_borrowing_book(self):
        result = borrowing_book(self.reader, self.book)
        self.assertEqual(result, 'Книга успешно взята.')

    def test_borrowing_unavailable_book(self):
        borrowing_book(self.reader, self.book)
        result = borrowing_book(self.reader, self.book)
        self.assertEqual(result, 'Книги нет в наличии.')

    def test_borrowing_max_books(self):
        book1 = Book.objects.create(title='Другая книга', 
                                    page_count=100, 
                                    publication_date=2023)
        book2 = Book.objects.create(title='Еще книга',
                                    page_count=100, 
                                    publication_date=2023)
        book3 = Book.objects.create(title='Еще одна книга',
                                    page_count=100, 
                                    publication_date=2023)
        borrowing_book(self.reader, book1)
        borrowing_book(self.reader, book2)   
        borrowing_book(self.reader, book3)   
        result = borrowing_book(self.reader, self.book)
        self.assertEqual(result, f'Читатель уже взял максимальное количество книг: {MAX_READER_BOOK}.')

class ReturningBookTestCase(TestCase):

    def setUp(self):
        self.reader = Reader.objects.create(name='Test reader')
        self.book = Book.objects.create(title='Test book', 
                                        page_count=100, 
                                        publication_date=2023)

        self.librarian = Librarian.objects.create(name='Test librarian')  
        self.hall = Hall.objects.create(librarian=self.librarian)
        
        # Создание стеллажей и полок
        for num_shelf in range(1, N_SHELF+1):
            shelf = Shelf.objects.create(number=num_shelf, hall=self.hall)
            for num_slot in range(1, N_SHELF_SLOT+1):
                ShelfSlot.objects.create(shelf=shelf, slot_number=num_slot)

        Borrow.objects.create(reader=self.reader, book=self.book, returned=False, borrow_date="2022-01-01", return_date="2022-02-01")


    def test_returning_book(self):
        result = returning_book(self.reader, self.book)
        self.assertEqual(result, 'Книга успешно возвращена.')
    
    def test_returning_no_free_space_book(self):

        # Заполняем полки книгами
        for shelf_slot in ShelfSlot.objects.all():
            for _ in range(N_BOOK_SLOT):
                extra_book = Book.objects.create(
                    title="Extra book",
                    author="Author",
                    page_count=100,
                    publication_date=2023,
                )
                BookShelf.objects.create(book=extra_book, shelf_slot=shelf_slot)

        result = returning_book(self.reader, self.book)
        self.assertEqual(result, "Все полки заняты.")
    
    def test_returning_unavailable_book(self):
        book1 = Book.objects.create(title='Другая книга', 
                                    page_count=100, 
                                    publication_date=2023)
        result = returning_book(self.reader, book1)
        self.assertEqual(result, 'Читатель не может вернуть книгу, которую не брал.')
    
    def test_returning_twice_book(self):
        returning_book(self.reader, self.book)
        result = returning_book(self.reader, self.book)
        self.assertEqual(result, 'Читатель уже вернул книгу.')

class SortingBooksTestCase(TestCase):

    def setUp(self):

        self.books = [Book.objects.create(title='B test book', 
                            page_count=100,
                            edition_type= 'AType',
                            publication_date=2023),
                     Book.objects.create(title='A test book', 
                            page_count=150, 
                            edition_type= 'AType',
                            publication_date=2021),
                     Book.objects.create(title='A test book', 
                            page_count=50, 
                            edition_type= 'BType',
                            publication_date=2022)]

        self.librarian = Librarian.objects.create(name='Test librarian')  
        self.hall = Hall.objects.create(librarian=self.librarian)
        
        # Создание стеллажей и полок
        for num_shelf in range(1, N_SHELF+1):
            shelf = Shelf.objects.create(number=num_shelf, hall=self.hall)
            for num_slot in range(1, N_SHELF_SLOT+1):
                ShelfSlot.objects.create(shelf=shelf, slot_number=num_slot)
        
        # Размещение книг на полках
        for book, shelf_slot in zip(self.books, ShelfSlot.objects.all()):
            BookShelf.objects.create(book=book, shelf_slot=shelf_slot)

    def test_sorting_book(self):
        sorted_books = Book.objects.all().order_by('edition_type', 'title', 'publication_date', 'page_count')
        sorting_books()

        for sorted_book, bookshelf in zip(sorted_books, BookShelf.objects.all()):
            self.assertEqual(sorted_book, bookshelf.book)

class BookMovementTestCase(TestCase):

    def setUp(self):
        self.book = Book.objects.create(title='Test book', 
                                        page_count=100, 
                                        publication_date=2023)

        self.librarian = Librarian.objects.create(name='Test librarian')  
        self.hall = Hall.objects.create(librarian=self.librarian)

        # Создание стеллажей и полок
        for num_shelf in range(1, N_SHELF+1):
            shelf = Shelf.objects.create(number=num_shelf, hall=self.hall)
            for num_slot in range(1, N_SHELF_SLOT+1):
                ShelfSlot.objects.create(shelf=shelf, slot_number=num_slot)
        
        # Размещение книги на полке
        BookShelf.objects.create(book=self.book, shelf_slot=ShelfSlot.objects.first())

    def test_bookmovement(self):

        # Случайная полка
        to_slot = ShelfSlot.objects.order_by('?')[0]
        bookmovement(book=self.book, to_slot=to_slot)

        result_record_bookshelf = ShelfSlot.objects.get(books=self.book)
        self.assertEqual(result_record_bookshelf, to_slot)
    
        result_record_to = BookMovement.objects.get(book=self.book).to_shelf_slot
        self.assertEqual(result_record_to, to_slot)
        
