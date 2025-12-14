# 🏛️ Library Management System (v1.0)

A robust, console-based **Library Management System** built with **Python** and **SQLite**. 
This project demonstrates backend development principles including **Object-Oriented Programming (OOP)**, **CRUD operations**, **Relational Database Logic**, and **Data Integrity**.

## 🚀 Key Features

* **Automatic ID Management:** Uses SQLite `AUTOINCREMENT` for both books and members to prevent manual entry errors and ensure uniqueness.
* **Data Integrity & Safe Delete:** Prevents the deletion of a member if they still have a borrowed book (Logic Check to prevent "Ghost Data").
* **Relational Database Logic:** Connects `Books` and `Members` tables dynamically using SQL JOINs.
* **Detailed Reporting:** View real-time status of books (Available / Borrowed by whom).
* **Persistent Storage:** All data is saved in a local SQLite database (`library.db`).

## 🛠️ Technologies Used

* **Language:** Python 3.x
* **Database:** SQLite3 (Built-in)
* **Paradigm:** Object-Oriented Programming (OOP)

## 📂 Project Structure

├── main.py          # The entry point of the application (Source Code)
├── library.db       # SQLite Database (Auto-generated on first run)
└── README.md        # Project Documentation

## ⚙️ How to Run

1.  **Clone the repository:**
    git clone https://github.com/farukkorkmaz-dev/Library-Management-System.git

2.  **Navigate to the project folder:**
    cd Library-Management-System

3.  **Run the application:**
    python main.py

## 📸 Example Workflow

1.  **Add a Member:** The system automatically assigns a unique Member ID.
2.  **Add a Book:** Books are registered with auto-generated IDs.
3.  **Borrow a Book:** Link a Book ID to a Member ID (Relational Logic).
4.  **Safe Delete Test:** Try deleting a member who currently has a book.
    * *Result:* The system will BLOCK this action to ensure data integrity!

## 🔮 Future Improvements

* Adding a Graphical User Interface (GUI) with Tkinter or PyQt.
* Migrating to a Web-based system using Flask or Django.
* Adding book categories and barcode scanning support.

---
**Developer:** Faruk Korkmaz (@farukkorkmaz-dev)
