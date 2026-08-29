# Block_Wise

Connecting tourists and locals through small-group authentic experiences with vibe filters, introvert-friendly capacity caps, and interactive map integrations.

## Backend Setup & Execution

The backend is built using Python, FastAPI, and SQLite.

### Prerequisites

Make sure you have Python 3.8+ installed on your system.

### 1. Install Dependencies

Navigate to the `server` directory and install the required dependencies:

```bash
cd server
pip install -r requirements.txt
```

### 2. Run the Server

Start the FastAPI development server using Uvicorn:

```bash
cd server
uvicorn main:app --reload
```

By default, the server runs on `http://127.0.0.1:8000`.

### 3. API Documentation

FastAPI automatically generates interactive Swagger API documentation. You can access it at:
* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
