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
        CREATE TABLE IF NOT EXISTS places (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            suburb TEXT NOT NULL,
            img TEXT,
            plate INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outings (
            id TEXT PRIMARY KEY,
            day INTEGER NOT NULL,
            host_id TEXT NOT NULL,
            place_id TEXT NOT NULL,
            starts_at TEXT NOT NULL,
            seats INTEGER NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            restrict_gender TEXT,
            restrict_age_bands TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rsvps (
            id TEXT PRIMARY KEY,
            outing_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            state TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            place_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            outing_id TEXT,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            outing_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            body TEXT NOT NULL,
            at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS txns (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            delta INTEGER NOT NULL,
            reason TEXT NOT NULL,
            outing_id TEXT,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            bio TEXT,
            gender TEXT,
            age_band TEXT,
            city TEXT,
            tags_followed TEXT,
            suspended_until TEXT,
            verified_at TEXT,
            face TEXT,
            noshows INTEGER
        )
    """)
    # We will drop the old events and users tables if they exist to start fresh
    cursor.execute("DROP TABLE IF EXISTS events")
    
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
class OutingCreate(BaseModel):
    id: str
    host_id: str
    day: int
    place_id: str
    starts_at: str
    seats: int
    status: str
    description: str
    tags: List[str]
    restrict_gender: Optional[str] = None
    restrict_age_bands: List[str]

class RsvpCreate(BaseModel):
    user_id: str
    state: str

class AttendanceUpdate(BaseModel):
    user_id: str
    status: str

# Helpers to map sqlite rows to dicts
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def serialize_row(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(row)

# Endpoints
@app.get("/api/state")
def get_state():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    state = {}
    
    # users
    cursor.execute("SELECT * FROM users")
    users = []
    for r in cursor.fetchall():
        d = serialize_row(r)
        d["tags_followed"] = json.loads(d["tags_followed"]) if d["tags_followed"] else []
        users.append(d)
    state["users"] = users
    
    # places
    cursor.execute("SELECT * FROM places")
    state["places"] = [serialize_row(r) for r in cursor.fetchall()]
    
    # outings
    cursor.execute("SELECT * FROM outings")
    outings = []
    for r in cursor.fetchall():
        d = serialize_row(r)
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        d["restrict_age_bands"] = json.loads(d["restrict_age_bands"]) if d["restrict_age_bands"] else []
        outings.append(d)
    state["outings"] = outings
    
    # rsvps
    cursor.execute("SELECT * FROM rsvps")
    state["rsvps"] = [serialize_row(r) for r in cursor.fetchall()]
    
    # comments
    cursor.execute("SELECT * FROM comments")
    state["comments"] = [serialize_row(r) for r in cursor.fetchall()]
    
    # messages
    cursor.execute("SELECT * FROM messages")
    state["messages"] = [serialize_row(r) for r in cursor.fetchall()]
    
    # txns
    cursor.execute("SELECT * FROM txns")
    state["txns"] = [serialize_row(r) for r in cursor.fetchall()]
    
    conn.close()
    return state

@app.post("/api/outings", status_code=status.HTTP_201_CREATED)
def create_outing(outing: OutingCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        tags_json = json.dumps(outing.tags)
        age_bands_json = json.dumps(outing.restrict_age_bands)
        cursor.execute(
            """
            INSERT INTO outings (id, day, host_id, place_id, starts_at, seats, status, description, tags, restrict_gender, restrict_age_bands)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (outing.id, outing.day, outing.host_id, outing.place_id, outing.starts_at, outing.seats, outing.status, outing.description, tags_json, outing.restrict_gender, age_bands_json)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create outing: {str(e)}"
        )
    conn.close()
    return {"message": "success"}

@app.post("/api/outings/{outing_id}/rsvp")
def rsvp_outing(outing_id: str, rsvp: RsvpCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check credits logic could be handled here or frontend.
        # Add rsvp
        rsvp_id = f"r_{int(datetime.now().timestamp())}"
        cursor.execute(
            "INSERT INTO rsvps (id, outing_id, user_id, state) VALUES (?, ?, ?, ?)",
            (rsvp_id, outing_id, rsvp.user_id, rsvp.state)
        )
        # Add txn for joining
        txn_id = f"t_{int(datetime.now().timestamp())}"
        cursor.execute(
            "INSERT INTO txns (id, user_id, delta, reason, outing_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (txn_id, rsvp.user_id, -1, "Joined outing", outing_id, datetime.now().strftime("%d %b"))
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    return {"message": "success"}

@app.post("/api/outings/{outing_id}/attendance")
def confirm_attendance(outing_id: str, updates: List[AttendanceUpdate]):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Mark outing as past
        cursor.execute("UPDATE outings SET status = 'past' WHERE id = ?", (outing_id,))
        
        # We need to deposit credits to the host for attending users, but the frontend also tracks `noshows`.
        # Simplified: we just record attendance in rsvps/txns as needed.
        for u in updates:
            if u.status == "attended":
                # Find host of this outing
                cursor.execute("SELECT host_id FROM outings WHERE id = ?", (outing_id,))
                host_row = cursor.fetchone()
                if host_row:
                    host_id = host_row["host_id"]
                    if host_id != u.user_id:
                        # Give host +1 credit for each attendee
                        txn_id = f"t_{int(datetime.now().timestamp())}_{u.user_id}"
                        cursor.execute(
                            "INSERT INTO txns (id, user_id, delta, reason, outing_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (txn_id, host_id, 1, "Hosted", outing_id, datetime.now().strftime("%d %b"))
                        )
            elif u.status == "no_show":
                # Increment noshows for user
                cursor.execute("UPDATE users SET noshows = noshows + 1 WHERE id = ?", (u.user_id,))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    conn.close()
    return {"message": "success"}
