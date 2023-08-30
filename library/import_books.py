from datetime import datetime
from lib.models import Book
import csv

# Авторы@Название издания@Вид издания@Год издания@Кол-во стр.@Срок окончания авторского договора@ISBN@Аннотация
# Дата публикации = срок окончания авторского договора
# Название книги = название издания

def import_books():
    with open('/Users/arina/projects/my_django/django_test_case/library/books.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='@')
        for row in reader:
            try:
                book = Book(
                    author = row['Авторы'],
                    title = row['Название издания'],
                    edition_type = row['Вид издания'],
                    number = row['ISBN'],
                    page_count = row['Кол-во стр.'],
                    publication_date = row['Год издания'],
                    description = row['Аннотация']
                )
                book.save()
            except:
                pass