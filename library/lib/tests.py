from django.test import TestCase
from lib.models import Book, Reader, Borrow
from lib.methods import borrowing_book, MAX_READER_BOOK
from django.utils import timezone
from datetime import timedelta

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