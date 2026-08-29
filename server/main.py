import json
import sqlite3
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# SQLite Database setup
DB_PATH = "events.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            tags TEXT,  -- JSON-serialized dictionary/string
            capacity INTEGER NOT NULL,
            location_name TEXT NOT NULL,
            lat REAL,   -- Nullable for now
            lng REAL    -- Nullable for now
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            bio TEXT,
            gender TEXT,
            dob TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize Database
init_db()

app = FastAPI(
    title="Block_Wise Backend API",
    description="API for connecting tourists and locals through small-group authentic experiences.",
    version="1.0.0"
)

# CORS middleware to allow requests from Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas for validation
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the event")
    tags: Dict[str, Any] = Field(default_factory=dict, description="Tags associated with the event vibes/types")
    capacity: int = Field(..., gt=0, description="Introvert-friendly capacity cap")
    location_name: str = Field(..., min_length=1, description="Location name string")
    lat: Optional[float] = Field(None, description="Latitude for Leaflet Map")
    lng: Optional[float] = Field(None, description="Longitude for Leaflet Map")

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

# User Pydantic Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, description="Public username")
    bio: Optional[str] = Field(None, description="Short bio")
    gender: Optional[str] = Field(None, description="Gender description")

class UserCreate(UserBase):
    dob: date = Field(..., description="Date of birth (YYYY-MM-DD)")

class UserResponse(UserBase):
    id: int
    age_range: str = Field(..., description="Public age range calculated from DOB")

# Helper to calculate public age range from date of birth
def calculate_age_range(dob_str: str) -> str:
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 18:
            return "Under 18"
        elif age <= 19:
            return "18-19"
        elif age <= 25:
            return "20-25"
        elif age <= 30:
            return "26-30"
        elif age <= 40:
            return "31-40"
        elif age <= 50:
            return "41-50"
        elif age <= 60:
            return "51-60"
        else:
            return "60+"
    except Exception:
        return "Unknown"

# Helpers to map sqlite rows to dicts
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def serialize_event(row: sqlite3.Row) -> Dict[str, Any]:
    event_dict = dict(row)
    # Parse tags JSON string back to dict
    try:
        event_dict["tags"] = json.loads(row["tags"]) if row["tags"] else {}
    except Exception:
        event_dict["tags"] = {}
    return event_dict

def serialize_user(row: sqlite3.Row) -> Dict[str, Any]:
    user_dict = dict(row)
    # Calculate age range from DOB
    user_dict["age_range"] = calculate_age_range(row["dob"])
    # Do not expose raw DOB publicly
    if "dob" in user_dict:
        del user_dict["dob"]
    return user_dict

# Endpoints
@app.get("/api/events", response_model=List[EventResponse])
def get_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    conn.close()
    return [serialize_event(row) for row in rows]

@app.get("/api/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    return serialize_event(row)

@app.post("/api/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        tags_json = json.dumps(event.tags)
        cursor.execute(
            """
            INSERT INTO events (title, tags, capacity, location_name, lat, lng)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event.title, tags_json, event.capacity, event.location_name, event.lat, event.lng)
        )
        conn.commit()
        event_id = cursor.lastrowid
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )
    
    # Retrieve the newly created event to ensure accuracy
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()
    return serialize_event(row)

@app.put("/api/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event: EventCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT id FROM events WHERE id = ?", (event_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
        
    try:
        tags_json = json.dumps(event.tags)
        cursor.execute(
            """
            UPDATE events
            SET title = ?, tags = ?, capacity = ?, location_name = ?, lat = ?, lng = ?
            WHERE id = ?
            """,
            (event.title, tags_json, event.capacity, event.location_name, event.lat, event.lng, event_id)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )
        
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()
    return serialize_event(row)

@app.delete("/api/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT id FROM events WHERE id = ?", (event_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
        
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return None

# User Endpoints
@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if username is already taken
    cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user.username}' is already taken"
        )
        
    try:
        # Save dob as string (YYYY-MM-DD)
        dob_str = user.dob.strftime("%Y-%m-%d")
        cursor.execute(
            """
            INSERT INTO users (username, bio, gender, dob)
            VALUES (?, ?, ?, ?)
            """,
            (user.username, user.bio, user.gender, dob_str)
        )
        conn.commit()
        user_id = cursor.lastrowid
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )
        
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return serialize_user(row)

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return serialize_user(row)

@app.get("/api/users", response_model=List[UserResponse])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [serialize_user(row) for row in rows]
