# Simple Notes REST API

A lightweight, high-performance CRUD (Create, Read, Update, Delete) backend built with **FastAPI**, **SQLAlchemy**, and **SQLite**. This project demonstrates the ability to build functional RESTful services with persistent database storage.

## 🚀 Key Features
- **Full CRUD Support**: Create, read, update, and delete notes seamlessly.
- **Persistent Storage**: Uses SQLite to save data locally in a `.db` file.
- **Interactive Documentation**: Built-in Swagger UI for real-time endpoint testing.
- **Clean Architecture**: Separation of concerns between models, database configuration, and API logic.

## 🛠 Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite
- **Server**: Uvicorn

## 📖 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/notes` | Create a new note (requires title and content) |
| GET | `/notes` | Retrieve a list of all saved notes |
| GET | `/notes/{id}` | Get details for a specific note by ID |
| PUT | `/notes/{id}` | Update an existing note's title or content |
| DELETE | `/notes/{id}` | Remove a note from the database |

## ⚙️ How to Run Locally
1. **Clone the repo**: `git clone <your-repo-link>`
2. **Setup Environment**: 
   - `python -m venv venv`
   - `.\venv\Scripts\activate` (Windows)
3. **Install Dependencies**: `pip install fastapi uvicorn sqlalchemy`
4. **Launch Server**: `uvicorn main:app --reload`
5. **Test**: Open `http://127.0.0.1:8000/docs` in your browser.