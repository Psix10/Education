from pydantic import BaseModel, field_validator
from typing import List, Optional, Callable, Any
import re
import functools
import datetime


class Book(BaseModel):
    title: str
    author: str
    year: int
    available: bool = True
    categories: List[str] = []
    give: str = "" 
    
    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v):
        if not isinstance(v, list):
            raise ValueError("Categories must be a list")
        for category in v:
            if not isinstance(category, str) or not category.strip():
                raise ValueError("Each category must be a non-empty string")
        return v


class User(BaseModel):
    name: str
    email: str
    membership_id: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class Library(BaseModel):
    books: List[Book] = []
    users: List[User] = []
    
    def total_books(self) -> int:
        return len(self.books)
    
    def all_users_view(self) -> str:
        for user in library.users:
            print(f"- {user.name} ({user.email}) - ID: {user.membership_id}")
                    

class BookNotAvailable(Exception):
    pass


def log_operation(operation_name: str = None):
    """
    Декоратор для логирования операций с книгами.
    
    Этот декоратор автоматически логирует:
    - Время начала операции
    - Название операции
    - Входные параметры (позиционные и именованные)
    - Результат выполнения или ошибку
    
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Получаем название операции
            op_name = operation_name or func.__name__
            
            # Получаем текущее время
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Логируем начало операции
            print(f"[{timestamp}] [START] Начало операции: {op_name}")
            
            # Логируем параметры
            if args:
                print(f"[{timestamp}] [INPUT] Параметры: {args}")
            if kwargs:
                print(f"[{timestamp}] [INPUT] Ключевые параметры: {kwargs}")
            
            try:
                # Выполняем функцию
                result = func(*args, **kwargs)
                
                # Логируем успешный результат
                if result is not None:
                    print(f"[{timestamp}] [SUCCESS] Результат: {result}")
                else:
                    print(f"[{timestamp}] [SUCCESS] Операция выполнена успешно")
                
                return result
                
            except Exception as e:
                # Логируем ошибку
                print(f"[{timestamp}] [ERROR] Ошибка в операции {op_name}: {str(e)}")
                raise
                
        return wrapper
    return decorator

@log_operation("Добавление книги")
def add_book(library: Library, title: str, author: str, year: int, 
            categories: List[str] = None, available: bool = True) -> Book:
    """Add a new book to the library."""
    if categories is None:
        categories = []
    
    book = Book(
        title=title,
        author=author,
        year=year,
        categories=categories,
        available=available
    )
    library.books.append(book)
    return book


@log_operation("Поиск книги")
def find_book(library: Library, title: str) -> Optional[Book]:
    """Find a book by title in the library."""
    for book in library.books:
        if book.title.lower() == title.lower():
            return book
    return None


@log_operation("Проверка доступности книги")
def is_book_borrow(book: Book) -> bool:
    """Check if a book is available for borrowing."""
    if book.available:
        return book.available
    else:
        raise BookNotAvailable("Book not available")
    

@log_operation("Возврат книги")
def return_book(book: Book) -> None:
    """Return a book to the library (make it available)."""
    book.available = True

@log_operation()
def get_library_stats(library: Library) -> dict:
    """Получить статистику библиотеки."""
    return {
        "total_books": len(library.books),
        "total_users": len(library.users),
        "available_books": sum(1 for book in library.books if book.available),
        "borrowed_books": sum(1 for book in library.books if not book.available)
    }

@log_operation("Получение информации о книге")
def get_book_info(book: Book) -> str:
    """Получить информацию о книге."""
    return f"'{book.title}' by {book.author} ({book.year}) - {'Available' if book.available else 'Borrowed'}"

@log_operation("Забрали книгу")
def giving(library: Library, id: int, borrowing_book: Book) -> None:
        for i in library.users:
            if i.membership_id == id:
                if borrowing_book.available == True:
                    print(f"\n{borrowing_book.give}\n")
                    borrowing_book.give = id
                else:
                    raise BookNotAvailable("Book not available")



if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    library = Library()
    
    add_book(library, "1984", "George Orwell", 1949, ["Dystopian", "Fiction"])
    add_book(library, "To Kill a Mockingbird", "Harper Lee", 1960, ["Fiction", "Drama"])
    add_book(library, "The Great Gatsby", "F. Scott Fitzgerald", 1925, ["Fiction", "Classic"])
    
    
    user1 = User(name="John Doe", email="john@example.com", membership_id="M001")
    user2 = User(name="Jane Smith", email="jane@example.com", membership_id="M002")
    library.users.extend([user1, user2])
    
    
    print(f"Total books in library: {library.total_books()}")
    
    
    found_book = find_book(library, "1984")
    if found_book:
        print(f"\nFound book: {found_book.title} by {found_book.author}")
        print(f"Is available for borrowing: {is_book_borrow(found_book)}")
        
        
        try:
            if is_book_borrow(found_book):
                found_book.available = False
        except BookNotAvailable:
            print("\nBook not available\n")
            
            return_book(found_book)
            print(f"Book '{found_book.title}' has been returned")
            print(f"Is available for borrowing: {is_book_borrow(found_book)}")
    
    
    print("\nAll books in library:")
    for book in library.books:
        print(f"- {book.title} by {book.author} ({book.year}) - Available: {book.available}")
        print(f"  Categories: {book.categories}\n")
    
    
    library.all_users_view()
    
    
    print("\n" + "="*50)
    print("ДЕМОНСТРАЦИЯ ОБРАБОТКИ ОШИБОК:")
    print("="*50)
    
    
    print("\nПоиск несуществующей книги:")
    found_book = find_book(library, "Несуществующая книга")
    if found_book:
        print(f"Найдена книга: {found_book.title}")
    else:
        print("Книга не найдена")
    
    print("\nПроверка доступности уже взятой книги:")
    
    try:
        
        book_to_borrow = find_book(library, "To Kill a Mockingbird")
        if book_to_borrow:
            book_to_borrow.available = False  
            print(f"Книга '{book_to_borrow.title}' взята")
            
            
            is_available = is_book_borrow(book_to_borrow)
            print(f"Доступность: {is_available}")
    except BookNotAvailable as e:
        print(f"Ошибка: {e}")
    
    
    print("\nВозврат книги:")
    return_book(book_to_borrow)
    print(f"Книга '{book_to_borrow.title}' возвращена")
    
    
    print("\n" + "="*50)
    print("ДЕМОНСТРАЦИЯ РАЗНЫХ НАСТРОЕК ДЕКОРАТОРА:")
    print("="*50)
    
    print("\nПолучение статистики библиотеки:")
    stats = get_library_stats(library)
    print(f"Статистика: {stats}")
    
    print("\nПолучение информации о книге:")
    book_info = get_book_info(library.books[0])
    print(f"Информация: {book_info}\n")

giving(library,"M001", book_to_borrow)

print("\nПолучение информации о книге:")
book_info = get_book_info(library.books[1])
print(f"Информация: {book_info}")

print("\nВозврат книги:")
return_book(book_to_borrow)
print(f"Книга '{book_to_borrow.title}' возвращена")


print("\nПолучение статистики библиотеки:")
stats = get_library_stats(library)
print(f"Статистика: {stats}")