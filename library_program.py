import psycopg2
import csv
from datetime import datetime

# Подключение к базе данных
def connect_to_database():
    connection = psycopg2.connect(
        database="library_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    return connection


# Добавление книги
def add_book(connection, title, author, genre):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Books (Title, Author, Genre) VALUES (%s, %s, %s)", (title, author, genre))
    connection.commit()
    cursor.close()


# Добавление читателя
def add_reader(connection, first_name, last_name, birthdate):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Readers (First_Name, Last_Name, Birthdate) VALUES (%s, %s, %s)", (first_name, last_name, birthdate))
    connection.commit()
    cursor.close()


# Добавление факта взятия книги
def add_book_borrowing(connection, book_id, reader_id, borrow_date):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Facts (Book_ID, Reader_ID, Borrow_Date) VALUES (%s, %s, %s)", (book_id, reader_id, borrow_date))
    connection.commit()
    cursor.close()


# Добавления факта возврата книги
def add_book_returning(connection, book_id, reader_id, return_date):
    cursor = connection.cursor()
    cursor.execute("UPDATE Facts SET Return_Date = %s WHERE Book_ID = %s AND Reader_ID = %s AND Return_Date IS NULL", (return_date, book_id, reader_id))
    connection.commit()
    cursor.close()


# Получение отчета о количестве книг в библиотеке
def get_books_count(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Books")
    count = cursor.fetchone()[0]
    cursor.close()
    return count


# Получение отчета о количестве читателей
def get_readers_count(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Readers")
    count = cursor.fetchone()[0]
    cursor.close()
    return count


# Получение отчета о количестве книг, взятых каждым читателем
def get_books_borrowed_by_reader(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT Readers.ID, Readers.First_Name, Readers.Last_Name, COUNT(Facts.Book_ID) "
                   "FROM Readers "
                   "LEFT JOIN Facts ON Readers.ID = Facts.Reader_ID "
                   "GROUP BY Readers.ID, Readers.First_Name, Readers.Last_Name")
    result = cursor.fetchall()
    cursor.close()
    return result


# Получение отчета о количестве книг на руках у каждого читателя
def get_books_on_hands_by_reader(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT Readers.ID, Readers.First_Name, Readers.Last_Name, COUNT(Facts.Book_ID) "
                   "FROM Readers "
                   "LEFT JOIN Facts ON Readers.ID = Facts.Reader_ID "
                   "WHERE Facts.Return_Date IS NULL "
                   "GROUP BY Readers.ID, Readers.First_Name, Readers.Last_Name")
    result = cursor.fetchall()
    cursor.close()
    return result


# Получение даты последнего посещения читателем библиотеки
def get_last_visit_date_by_reader(connection, reader_id):
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(Borrow_Date) FROM Facts WHERE Reader_ID = %s", (reader_id,))
    date = cursor.fetchone()[0]
    cursor.close()
    return date


# Получение самого читаемого автора
def get_most_read_author(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT Author, COUNT(*) "
                   "FROM Books "
                   "GROUP BY Author "
                   "ORDER BY COUNT(*) DESC "
                   "LIMIT 1")
    author, count = cursor.fetchone()
    cursor.close()
    return author


# Получение самых предпочитаемых читателями жанров
def get_most_preferred_genres(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT Genre, COUNT(*) "
                   "FROM Books "
                   "GROUP BY Genre "
                   "ORDER BY COUNT(*) DESC")
    result = cursor.fetchall()
    cursor.close()
    return result


# Получение любимого жанра каждого читателя
def get_favorite_genre_by_reader(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT Reader_ID, Genre, COUNT(*) AS cnt FROM Facts JOIN Books ON Facts.Book_ID = Books.ID "
                   "GROUP BY Reader_ID, Genre ORDER BY COUNT(*) DESC")
    result = cursor.fetchall()
    cursor.close()

    # Отобразить только один любимый жанр для каждого читателя
    favorites = {}
    for reader_id, genre, count in result:
        if reader_id not in favorites:
            favorites[reader_id] = {'Genre': genre, 'Count': count}

    # Конвертировать словарь в список для согласованности вывода
    favorites_list = [(k, v['Genre'], v['Count']) for k, v in favorites.items()]

    return favorites_list


# Удаление книги
def delete_book(connection, book_id):
    cursor = connection.cursor()
    # Удаляем связанные записи в 'facts'
    cursor.execute("DELETE FROM facts WHERE book_id = %s", (book_id,))
    # Удаляем книгу
    cursor.execute("DELETE FROM Books WHERE ID = %s", (book_id,))
    connection.commit()
    cursor.close()


# Изменение книги
def update_book(connection, book_id, new_title, new_author, new_genre):
    cursor = connection.cursor()
    cursor.execute("UPDATE Books SET Title = %s, Author = %s, Genre = %s WHERE ID = %s",
                   (new_title, new_author, new_genre, book_id))
    connection.commit()
    cursor.close()


# Удаление читателя
def delete_reader(connection, reader_id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Readers WHERE ID = %s", (reader_id,))
    connection.commit()
    cursor.close()


# Изменение читателя
def update_reader(connection, reader_id, new_first_name, new_last_name, new_birthdate):
    cursor = connection.cursor()
    cursor.execute("UPDATE Readers SET First_Name = %s, Last_Name = %s, Birthdate = %s WHERE ID = %s",
                   (new_first_name, new_last_name, new_birthdate, reader_id))
    connection.commit()
    cursor.close()


#Эта функция будет генерировать CSV-файл с информацией о читателях, которые не вернули книги вовремя.
# Этот файл можно затем использовать для печати.
def generate_report_on_late_returns(connection):
    cursor = connection.cursor()
    today = datetime.today().date()
    # Запрашиваем всех читателей и книги, которые они не вернули вовремя
    cursor.execute("SELECT Readers.ID, Readers.First_Name, Readers.Last_Name, Books.Title, Facts.Expected_Return_Date "
                   "FROM Facts "
                   "JOIN Readers ON Facts.Reader_ID = Readers.ID "
                   "JOIN Books ON Facts.Book_ID = Books.ID "
                   "WHERE Facts.Return_Date IS NULL AND Facts.Expected_Return_Date < %s",
                   (today,))
    overdue_records = cursor.fetchall()
    cursor.close()

    # Записываем результаты в файл
    with open('overdue_report.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Reader_ID", "First_Name", "Last_Name", "Book_Title", "Expected_Return_Date"])
        for record in overdue_records:
            writer.writerow(record)


# Обработка ошибок
try:
    db_connection = connect_to_database()

    while True:
        print("\nВыберите действие:")
        print("1. Добавить/Удалить/Изменить книгу")
        print("2. Добавить/Удалить/Изменить читателя")
        print("3. Добавить факт взятия/возврата книги")
        print("4. Получить отчет")
        print("5. Сгенерировать отчет о просроченных возвратах")
        print("6. Выйти")
        choice = input("Ваш выбор: ")

        if choice == "1":
            print("1. Добавить книгу")
            print("2. Удалить книгу")
            print("3. Изменить книгу")
            sub_choice = input("Ваш выбор: ")
            if sub_choice == "1":
                title = input("Название книги: ")
                author = input("Автор: ")
                genre = input("Жанр: ")
                add_book(db_connection, title, author, genre)
            elif sub_choice == "2":
                book_id = input("ID книги для удаления: ")
                delete_book(db_connection, book_id)
            elif sub_choice == "3":
                book_id = input("ID книги для изменения: ")
                new_title = input("Новое название книги: ")
                new_author = input("Новый автор: ")
                new_genre = input("Новый жанр: ")
                update_book(db_connection, book_id, new_title, new_author, new_genre)

        # Соответствующий код для пользователей и фактов взятия/возврата книг
        elif choice == "2":
            print("Выберите действие:")
            print("1. Добавить читателя")
            print("2. Удалить читателя")
            print("3. Изменить читателя")
            action_choice = input("Ваш выбор: ")

            if action_choice == "1":
                first_name = input("Введите имя читателя: ")
                last_name = input("Введите фамилию читателя: ")
                birthdate = input("Введите дату рождения читателя: ")
                add_reader(db_connection, first_name, last_name, birthdate)
                print("Читатель успешно добавлен.")
            if action_choice == "2":
                reader_id = input("Введите id читателя:")
                delete_reader(db_connection, reader_id)
            if action_choice == "3":
                reader_id = input("Введите id читателя:")
                new_first_name = input("Введите имя читателя: ")
                new_last_name = input("Введите фамилию читателя: ")
                new_birthdate = input("Введите дату рождения читателя: ")
                update_reader(db_connection, reader_id, new_first_name, new_last_name, new_birthdate)
        elif choice == "3":
            print("1. Добавить факт взятия книги")
            print("2. Добавить факт возврата книги")
            sub_choice = input("Ваш выбор: ")
            if sub_choice == "1":
                book_id = input("ID книги: ")
                reader_id = input("ID читателя: ")
                borrow_date = input("Дата взятия: ")
                add_book_borrowing(db_connection, book_id, reader_id, borrow_date)
            elif sub_choice == "2":
                book_id = input("ID книги: ")
                reader_id = input("ID читателя: ")
                return_date = input("Дата возврата: ")
                add_book_returning(db_connection, book_id, reader_id, return_date)

        elif choice == "4":
            print("1. Получить общее кол-во книг и читателей")
            print("2. Получить кол-во взятых каждым читателем книг")
            print("3. Сколько книг сейчас на руках у каждого читателя ")
            print("4. Дата последнего посещения читателем библиотеки")
            print("5. Самый читаемый автор")
            print("6. Самые предпочитаемые читателями жанры")
            print("7. Любимый жанр каждого читателя")
            sub_choice = input("Ваш выбор: ")
            if sub_choice == "1":
                num_books = get_books_count(db_connection)
                num_readers = get_readers_count(db_connection)
                print(f"Количество книг: {num_books}, количество читателей: {num_readers}")
            elif sub_choice == "2":
                book_counts = get_books_borrowed_by_reader(db_connection)
                for reader_id, fname, lname, num_books in book_counts:
                    print(f"[Reader ID: {reader_id}, Имя: {fname}, Фамилия: {lname}]: Взято книг - {num_books}")
            elif sub_choice == "3":
                book_counts = get_books_on_hands_by_reader(db_connection)
                for reader_id, fname, lname, num_books in book_counts:
                    print(f"[Reader ID: {reader_id}, Имя: {fname}, Фамилия: {lname}]: Книг на руках - {num_books}")
            elif sub_choice == "4":
                reader_id = input("ID читателя: ")
                last_visit_date = get_last_visit_date_by_reader(db_connection, reader_id)
                print(f"Дата последнего посещения библиотеки читателем с ID {reader_id}: {last_visit_date}")
            elif sub_choice == "5":
                most_read_author = get_most_read_author(db_connection)
                print(f"Самый читаемый автор: {most_read_author}")
            elif sub_choice == "6":
                most_preferred_genres = get_most_preferred_genres(db_connection)
                print("Самые предпочитаемые читателями жанры по убыванию:")
                for genre, count in most_preferred_genres:
                    print(f"Жанр: {genre}, количество: {count}")
            elif sub_choice == "7":
                favorite_genres = get_favorite_genre_by_reader(db_connection)
                for reader_id, genre, count in favorite_genres:
                    print(
                        f"[Reader ID: {reader_id}]: Любимый жанр - {genre}, количество взятых книг этого жанра - {count}")

        elif choice == "5":
            generate_report_on_late_returns(db_connection)
            print("Отчет о просроченных возвратах сгенерирован и сохранен в файл 'overdue_report.csv'")

        elif choice == "6":
            break
        else:
            print("Неизвестная операция")

except Exception as e:
    print(f"Ошибка: {e}")

