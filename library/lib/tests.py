from django.test import TestCase
from lib.models import Book, Reader, Librarian, Hall, Shelf, ShelfSlot, Borrow
from lib.methods import borrowing_book, MAX_READER_BOOK
from lib.methods import returning_book
from lib.models import N_SHELF, N_SHELF_SLOT

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
    
