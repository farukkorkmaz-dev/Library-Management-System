import sqlite3

class Library:
    def __init__(self):
        self.connect_db()

    def connect_db(self):
        self.connection = sqlite3.connect("library.db")
        self.cursor = self.connection.cursor()
        
        # 1. BOOKS TABLE
        query_books = """CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT, 
            author TEXT, 
            publisher TEXT, 
            pages INT, 
            owner_id INT
        )"""
        self.cursor.execute(query_books)
        
        # 2. MEMBERS TABLE
        query_members = """CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            surname TEXT
        )"""
        self.cursor.execute(query_members)
        self.connection.commit()

    def close_connection(self):
        self.connection.close()

    # --- LIST OPERATIONS ---
    def list_books(self):
        self.cursor.execute("SELECT * FROM books")
        book_list = self.cursor.fetchall()
        print("\n--- 📚 BOOK LIST ---")
        if len(book_list) == 0:
            print("Library is empty.")
        else:
            for book in book_list:
                # book[0]=id, book[1]=title
                print(f"[ID: {book[0]}] {book[1]} - {book[2]} ({book[4]} p.)")

    def list_members(self):
        self.cursor.execute("SELECT * FROM members")
        member_list = self.cursor.fetchall()
        print("\n--- 👥 MEMBER LIST ---")
        if len(member_list) == 0:
           print("No members found.")
        else:
            for member in member_list:
                print(f"[Member ID: {member[0]}] {member[1]} {member[2]}")

    # --- ADD OPERATIONS ---
    def add_member(self, name, surname):
        query = "INSERT INTO members (name, surname) VALUES(?, ?)"
        self.cursor.execute(query, (name, surname))    
        self.connection.commit()
        print(f"✅ New member added: {name} {surname}")

    def add_book(self, title, author, publisher, pages):
        query = "INSERT INTO books (title, author, publisher, pages, owner_id) VALUES(?,?,?,?,?)"
        self.cursor.execute(query, (title, author, publisher, pages, None))
        self.connection.commit() 
        print(f"✅ Book added: {title}")

    # --- DELETE & UPDATE ---
    def delete_book(self, book_id): 
        query = "DELETE FROM books WHERE id = ?"
        self.cursor.execute(query, (book_id,))
        self.connection.commit()
        print(f"🗑️ Book (ID: {book_id}) deleted.")

    # --- NEW: SAFE DELETE MEMBER ---
    def delete_member(self, member_id):
        # 1. Check if member exists
        self.cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        if len(self.cursor.fetchall()) == 0:
            print("❌ Member not found.")
            return

        # 2. CRITICAL CHECK: Does this member have any books?
        self.cursor.execute("SELECT * FROM books WHERE owner_id = ?", (member_id,))
        borrowed_books = self.cursor.fetchall()
        
        if len(borrowed_books) > 0:
            print(f"❌ CANNOT DELETE MEMBER! They still have {len(borrowed_books)} book(s).")
            print("Please return the books first.")
            return

        # 3. Safe to delete
        query = "DELETE FROM members WHERE id = ?"
        self.cursor.execute(query, (member_id,))
        self.connection.commit()
        print(f"✅ Member (ID: {member_id}) deleted successfully.")

    def update_pages(self, book_id, new_pages):
        query = "UPDATE books SET pages = ? WHERE id = ?"
        self.cursor.execute(query, (new_pages, book_id))
        self.connection.commit()
        print(f"🔄 Book (ID: {book_id}) updated.")

    # --- LOAN OPERATIONS ---
    def borrow_book(self, book_id, member_id):
        self.cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = self.cursor.fetchall()
        if len(book) == 0:
            print("❌ Invalid Book ID!")
            return
        
        self.cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = self.cursor.fetchall()
        if len(member) == 0:
            print(f"❌ Member ID {member_id} not found!")
            return

        if book[0][5] is not None:
            print("❌ This book is already borrowed.")
            return
            
        query = "UPDATE books SET owner_id = ? WHERE id = ?"
        self.cursor.execute(query, (member_id, book_id))
        self.connection.commit()
        print(f"✅ Success: Book {book_id} given to Member {member_id}.")

    def return_book(self, book_id):
        self.cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = self.cursor.fetchall()
        if len(book) == 0:
            print("❌ Invalid Book ID!")
            return
        if book[0][5] is None:
            print("❌ This book is already in the library.")
            return
        
        query = "UPDATE books SET owner_id = NULL WHERE id = ?"
        self.cursor.execute(query, (book_id,))
        self.connection.commit()
        print(f"✅ Book {book_id} returned to shelf.")

    def list_book_status(self):
        query = """
        SELECT books.id, books.title, members.name, members.surname 
        FROM books 
        LEFT JOIN members ON books.owner_id = members.id
        """
        self.cursor.execute(query)
        full_list = self.cursor.fetchall()
        print("\n--- 🔍 DETAILED STATUS ---")
        if len(full_list) == 0:
            print("Library is empty.")
        else:
            for item in full_list:
                b_id = item[0]
                title = item[1]
                m_name = item[2]
                m_surname = item[3]
                
                if m_name is None:
                    print(f"📕 [ID: {b_id}] {title} -> AVAILABLE")
                else:
                    print(f"⛔ [ID: {b_id}] {title} -> Borrowed by {m_name} {m_surname}")

# --- MAIN MENU ---

library = Library()
print("\n=== 🏛️  LIBRARY MANAGEMENT SYSTEM v1.0 (Global Final) ===")

while True:
    print("\n" + "="*30)
    print("MAIN MENU")
    print("1. 📚 Book Operations")
    print("2. 👥 Member & Loan Operations")
    print("q. Quit")
    print("="*30)
    
    choice = input("Select: ")

    if choice == "q":
        library.close_connection()
        print("Goodbye!")
        break

    # BOOK MENU
    elif choice == "1":
        while True:
            print("\n--- Book Management ---")
            print("1- List Books | 2- Add Book | 3- Delete Book | 4- Update Page | b- Back")
            action = input("Action: ")
            
            if action == "b": break 
            elif action == "1":
                library.list_books()
            elif action == "2":
                t = input("Title: ")
                a = input("Author: ")
                p = input("Publisher: ")
                try:
                    pg = int(input("Pages: "))
                    library.add_book(t, a, p, pg)
                except ValueError:
                    print("Invalid number.")
            elif action == "3":
                library.list_books() 
                try:
                    b_id = int(input("Enter Book ID to delete: "))
                    library.delete_book(b_id)
                except ValueError:
                    print("Please enter a numeric ID.")
            elif action == "4":
                library.list_books()
                try:
                    b_id = int(input("Enter Book ID: "))
                    new_pg = int(input("New Page Count: "))
                    library.update_pages(b_id, new_pg)
                except ValueError:
                    print("Please enter numbers.")

    # MEMBER MENU
    elif choice == "2":
        while True:
            print("\n--- Member & Loans ---")
            print("1- List Members | 2- Add Member | 3- Delete Member")
            print("4- Borrow Book | 5- Return Book | 6- Status Report | b- Back")
            action = input("Action: ")
            
            if action == "b": break
            elif action == "1":
                library.list_members()
            elif action == "2":
                n = input("Name: ")       
                s = input("Surname: ")
                library.add_member(n, s)
            
            # NEW FEATURE: Delete Member
            elif action == "3":
                library.list_members()
                try:
                    m_id = int(input("Enter Member ID to delete: "))
                    library.delete_member(m_id)
                except ValueError:
                    print("Invalid ID.")

            elif action == "4":
                library.list_books()
                try:
                    b_id = int(input("Enter Book ID: "))
                    m_id = int(input("Enter Member ID: "))
                    library.borrow_book(b_id, m_id)
                except ValueError:
                    print("Please enter numeric IDs.")
            elif action == "5":
                try:
                    b_id = int(input("Enter Book ID to return: "))
                    library.return_book(b_id)
                except ValueError:
                    print("Invalid ID.")
            elif action == "6":
                library.list_book_status()
