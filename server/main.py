import json
import sqlite3
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
