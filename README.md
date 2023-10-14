## Приложение для работы с БД "library_db"

Для запуска этого скрипта и его подключения к базе данных PostgreSQL, выполните следующие шаги:

1. Установите PostgreSQL: Если у вас еще не установлен PostgreSQL, убедитесь, что вы сначала 
установили его на своем компьютере. Вы также должны иметь базу данных PostgreSQL с 
именем "library_db". Для работы с БД используйте pgAdmin 4. Создайте базу данных с помощью команды:
```sh
CREATE DATABASE library_db
```
Затем в базе данных создайте таблицы командами:
```sh
CREATE TABLE public.books
(
    id serial PRIMARY KEY,
    title character varying(255) NOT NULL,
    author character varying(100) NOT NULL,
    genre character varying(100)
);
```
```sh
CREATE TABLE public.readers
(
    id serial PRIMARY KEY,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    birthdate date
);
```
```sh
CREATE TABLE public.facts
(
    id serial PRIMARY KEY,
    book_id integer REFERENCES public.books (id) NOT NULL,
    reader_id integer REFERENCES public.readers (id) NOT NULL,
    borrow_date date NOT NULL,
    return_date date,
    expected_return_date date
);
```
2. #### Установить зависимости

Используйте `pip` (или `pip3`, есть конфликт с Python2) для установки 
зависимостей:

```sh
pip install -r requirements.txt
```
3. Замените значения your_user и your_password в коде на ваши учетные данные PostgreSQL. Укажите имя пользователя и 
пароль, которые имеют доступ к базе данных.
4. Запустите скрипт: Откройте командную строку или терминал, перейдите в каталог, в котором находится ваш файл 
library_program.py, и запустите его:
```sh
python library_program.py
```
5. Используйте меню: После запуска скрипта вы увидите меню с различными действиями. Выберите действие, которое вы 
хотите выполнить, и следуйте инструкциям, вводя необходимые данные.
6. Подключение к базе данных: Скрипт будет подключаться к базе данных PostgreSQL с использованием учетных данных, 
которые вы предоставили в коде, и выполнять операции с базой данных в соответствии с вашими выборами.


Обратите внимание, что перед запуском этого скрипта необходимо убедиться, что PostgreSQL работает и база данных 
"library_db" с необходимыми таблицами создана и настроена правильно. Также, удостоверьтесь, что вы используете 
корректные учетные данные для подключения к базе данных в коде скрипта.