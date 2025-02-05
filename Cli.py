import requests

BASE_URL = "http://127.0.0.1:8000"
session = {"member_id": None, "role": None}

def register():
    """Register a new user"""
    name = input("Enter name: ")
    password = input("Enter password: ")
    role = input("Enter role (librarian/member): ").lower()
    
    response = requests.post(f"{BASE_URL}/register/", json={"name": name, "password": password, "role": role})
    print(response.json())

def login():
    """User login"""
    name = input("Enter name: ")
    password = input("Enter password: ")
    
    response = requests.post(f"{BASE_URL}/login/?name={name}&password={password}")
    if response.status_code == 200:
        session.update(response.json())
        print("\n✅ Login successful!")
    else:
        print("\n❌ Login failed! Invalid credentials.")

def logout():
    """Logout the user"""
    session["member_id"] = None
    session["role"] = None
    print("\n✅ Logged out successfully!")

def add_book():
    """Librarians can add books"""
    if session["role"] != "librarian":
        print("\n❌ Only librarians can add books.")
        return
    
    title = input("Enter book title: ")
    author = input("Enter book author: ")
    isbn = input("Enter ISBN: ")
    
    response = requests.post(f"{BASE_URL}/books/", json={"title": title, "author": author, "isbn": isbn})
    print(response.json())

def list_books():
    """List all books in the library"""
    response = requests.get(f"{BASE_URL}/books/list/")
    books = response.json()
    print("\n Available Books:")
    for book in books:
        print(f"  {book['id']}: {book['title']} by {book['author']} - {'✅ Available' if book['available'] else '❌ Borrowed'}")

def borrow_book():
    """Borrow a book"""
    if not session["member_id"]:
        print("\n❌ Please login first.")
        return
    
    book_id = int(input("Enter book ID to borrow: "))
    return_date = input("Enter return date (YYYY-MM-DD): ")
    
    response = requests.post(f"{BASE_URL}/borrow/", json={
        "member_id": session["member_id"], 
        "book_id": book_id, 
        "return_date": return_date
    })
    print(response.json())

def return_book():
    """Return a borrowed book"""
    if not session["member_id"]:
        print("\n❌ Please login first.")
        return

    book_id = int(input("Enter book ID to return: "))
    
    response = requests.post(f"{BASE_URL}/return/", json={
        "member_id": session["member_id"], 
        "book_id": book_id
    })
    print(response.json())

def search_books():
    """Search books by title or author"""
    if not session["member_id"]:
        print("\n❌ Please login first.")
        return

    query = input("Enter book title or author to search: ")
    response = requests.get(f"{BASE_URL}/books/list/")
    books = response.json()
    
    results = [book for book in books if query.lower() in book["title"].lower() or query.lower() in book["author"].lower()]
    
    print("\n🔎 Search Results:")
    for book in results:
        print(f"  {book['id']}: {book['title']} by {book['author']} - {'✅ Available' if book['available'] else '❌ Borrowed'}")

def list_borrowed_books():
    """List all books borrowed by the logged-in member"""
    if not session["member_id"]:
        print("\n❌ Please login first.")
        return

    response = requests.get(f"{BASE_URL}/borrowed_books/{session['member_id']}/")
    borrowed_books = response.json()

    if not borrowed_books:
        print("\n❌ No borrowed books found.")
    else:
        print("\n Borrowed Books:")
        for borrowed in borrowed_books:
            print(f"  {borrowed['book_id']}: {borrowed['title']} - Return Date: {borrowed['return_date']}")

def menu():
    """CLI Menu"""
    print("\n Welcome to Library Management System ")
    
    # Show book list at start
    list_books()
    
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Enter choice: ")
        
        if choice == "1":
            register()
        elif choice == "2":
            login()
            break  # Proceed to main menu after login
        elif choice == "3":
            print("\n Exiting...")
            return
        else:
            print("\n❌ Invalid choice! Try again.")

    while session["member_id"]:  # Main menu after login
        print("\n🔹 MAIN MENU 🔹")
        print("1. List Books")
        print("2. Search Books")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. List Borrowed Books")
        if session["role"] == "librarian":
            print("6. Add Book")
        print("7. Logout")
        
        choice = input("\nEnter choice: ")
        
        if choice == "1":
            list_books()
        elif choice == "2":
            search_books()
        elif choice == "3":
            borrow_book()
        elif choice == "4":
            return_book()
        elif choice == "5":
            list_borrowed_books()
        elif choice == "6" and session["role"] == "librarian":
            add_book()
        elif choice == "7":
            logout()
            break
        else:
            print("\n❌ Invalid choice! Try again.")

if __name__ == "__main__":
    menu()
  
