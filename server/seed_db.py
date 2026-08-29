import sqlite3
import json
import os
from main import init_db

# Ensure we are in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Run schema initialization to create tables
init_db()

IMG = {
  "matcha" : "https://www.figma.com/api/mcp/asset/4e656563-60d0-4540-ad55-32e1a835ff75.png",
  "hike"   : "https://www.figma.com/api/mcp/asset/4b77a23b-b573-460f-b46b-3640ab483164.png",
  "pottery": "https://www.figma.com/api/mcp/asset/fde7e80f-3fbd-4ddb-b4d0-1d2bed2e01a8.png",
  "face1"  : "https://www.figma.com/api/mcp/asset/83fb43ca-7501-4234-95c7-0102fd70afed.png",
  "face2"  : "https://www.figma.com/api/mcp/asset/a6f46b84-2fff-4dc6-8cd1-622fc7607768.png",
  "face3"  : "https://www.figma.com/api/mcp/asset/f863ac46-07fc-4c50-9abf-f731d5f78e16.png"
}

users = [
    { "id":"u1", "username":"wombatpost",  "bio":"chasing the perfect matcha", "age_band":"20-24", "gender":"F", "city":"Sydney",
      "tags_followed":["matchacafe","coffee","thrifting","art"], "suspended_until":None, "verified_at":"2026-03-02", "face":IMG["face1"], "noshows":2 },
    { "id":"u2", "username":"slowlaps",    "bio":"swims before work, always",   "age_band":"25-29", "gender":"M", "city":"Sydney",
      "tags_followed":["swimming","coffee","hiking"], "suspended_until":None, "verified_at":"2026-02-11", "face":IMG["face2"], "noshows":0 },
    { "id":"u3", "username":"ninetysix",   "bio":"walks the coast every Sunday", "age_band":"30s", "gender":"F", "city":"Sydney",
      "tags_followed":["hiking","swimming","bookshops"], "suspended_until":None, "verified_at":"2026-01-30", "face":IMG["face3"], "noshows":0 },
    { "id":"u4", "username":"tuesdaybest", "bio":"here for the noodles",        "age_band":"20-24", "gender":"M", "city":"Sydney",
      "tags_followed":["food","markets","nightlife"], "suspended_until":None, "verified_at":"2026-04-18", "face":None, "noshows":1 }
]

places = [
    { "id":"p1", "name":"Cornersmith",            "address":"Illawarra Rd",   "suburb":"Marrickville", "img":IMG["matcha"],  "plate":0 },
    { "id":"p2", "name":"Coogee to Bondi track",  "address":"Arden St",       "suburb":"Coogee",       "img":IMG["hike"],    "plate":1 },
    { "id":"p3", "name":"Anzac Park pottery shed","address":"Ernest St",      "suburb":"Cammeray",     "img":IMG["pottery"], "plate":2 },
    { "id":"p4", "name":"Tan Viet",               "address":"John St",        "suburb":"Cabramatta",   "img":None,        "plate":3 },
    { "id":"p5", "name":"Black Star Pastry",      "address":"Australia St",   "suburb":"Newtown",      "img":None,        "plate":0 },
    { "id":"p6", "name":"Addison Road Markets",   "address":"Addison Rd",     "suburb":"Marrickville", "img":None,        "plate":2 },
    { "id":"p7", "name":"Bondi Icebergs",         "address":"Notts Ave",      "suburb":"Bondi Beach",  "img":None,        "plate":1 }
]

outings = [
    { "id":"o1", "day":14, "host_id":"u1", "place_id":"p1", "starts_at":"Sat 14:00", "seats":5, "status":"upcoming",
      "description":"Three matcha places on one street. We start at Cornersmith and walk it out. I order for the table if you have no idea what to get.",
      "tags":["matchacafe","coffee"], "restrict_gender":None, "restrict_age_bands":[] },
    { "id":"o2", "day":15, "host_id":"u3", "place_id":"p2", "starts_at":"Sun 10:00", "seats":5, "status":"upcoming",
      "description":"Full coast walk, slow pace, coffee at the far end. Swim if the water is behaving.",
      "tags":["hiking","swimming"], "restrict_gender":"F", "restrict_age_bands":[] },
    { "id":"o3", "day":22, "host_id":"u4", "place_id":"p3", "starts_at":"Sun 10:00", "seats":4, "status":"upcoming",
      "description":"The shed runs a walk-in wheel session. No experience needed, everything you make is bad and that is the point.",
      "tags":["art"], "restrict_gender":None, "restrict_age_bands":[] },
    { "id":"o4", "day":20, "host_id":"u4", "place_id":"p4", "starts_at":"Fri 18:30", "seats":5, "status":"upcoming",
      "description":"Crispy chicken noodles, then a lap of the John St shops for dessert. Cabramatta is a 50 minute train and worth every minute.",
      "tags":["food","markets"], "restrict_gender":None, "restrict_age_bands":[] },
    { "id":"o5", "day":14, "host_id":"u2", "place_id":"p7", "starts_at":"Sat 06:15", "seats":5, "status":"upcoming",
      "description":"Sunrise lap before the pool fills up. Bring goggles, we get coffee after.",
      "tags":["swimming","coffee"], "restrict_gender":None, "restrict_age_bands":["20-24","25-29","30s"] },
    { "id":"o6", "day":21, "host_id":"u2", "place_id":"p5", "starts_at":"Sat 11:00", "seats":4, "status":"upcoming",
      "description":"Matcha and a strawberry watermelon cake, then the op shops down King St.",
      "tags":["matchacafe","thrifting"], "restrict_gender":None, "restrict_age_bands":[] },
    { "id":"o0", "day":2, "host_id":"u1", "place_id":"p6", "starts_at":"Last Sunday 09:00", "seats":5, "status":"past",
      "description":"Market lap then matcha at the far end of the shed.",
      "tags":["markets","matchacafe"], "restrict_gender":None, "restrict_age_bands":[] }
]

rsvps = [
    { "id":"r1", "outing_id":"o1", "user_id":"u2", "state":"rsvp" },
    { "id":"r2", "outing_id":"o1", "user_id":"u4", "state":"rsvp" },
    { "id":"r3", "outing_id":"o2", "user_id":"u1", "state":"rsvp" },
    { "id":"r4", "outing_id":"o4", "user_id":"u2", "state":"rsvp" },
    { "id":"r5", "outing_id":"o6", "user_id":"u3", "state":"rsvp" },
    { "id":"r6", "outing_id":"o0", "user_id":"u2", "state":"rsvp" },
    { "id":"r7", "outing_id":"o0", "user_id":"u3", "state":"rsvp" },
    { "id":"r8", "outing_id":"o0", "user_id":"u4", "state":"rsvp" }
]

comments = [
    { "id":"c1", "place_id":"p1", "user_id":"u2", "outing_id":None, "body":"The matcha is the reason to come but get the seeded loaf too. Tiny room, maybe eight seats, so a group of five is pushing it. Go on a weekday if you can.", "created_at":"12 Aug" },
    { "id":"c2", "place_id":"p1", "user_id":"u3", "outing_id":None, "body":"Ordered the ceremonial grade because someone told me to and I still don't fully know what that means, but it was very good and they were patient about explaining it.", "created_at":"3 Aug" },
    { "id":"c3", "place_id":"p1", "user_id":"u4", "outing_id":None, "body":"Cash is fine, card is fine, the queue moves. Sit at the window bench.", "created_at":"28 Jul" },
    { "id":"c4", "place_id":"p2", "user_id":"u1", "outing_id":None, "body":"Do it the Coogee to Bondi way, not the other direction. The last stretch downhill into Bondi is much better than grinding up it.", "created_at":"9 Aug" }
]

messages = [
    { "id":"m1", "outing_id":"o1", "user_id":"u2", "body":"Do we need to book or is it walk in? Happy to get there early and hold the bench.", "at":"Tue" },
    { "id":"m2", "outing_id":"o1", "user_id":"u1", "body":"Walk in is fine at 2pm, it empties out after lunch. Meet me out the front, I'll be the one holding a tote bag.", "at":"Tue" },
    { "id":"m3", "outing_id":"o1", "user_id":"u4", "body":"Coming from Cabramatta so might be five minutes late. Start without me.", "at":"Wed" },
    { "id":"m4", "outing_id":"o2", "user_id":"u1", "body":"Is the water usually calm enough to swim at the end?", "at":"Thu" }
]

txns = [
    { "id":"t1", "user_id":"u1", "delta":+3, "reason":"Starter credits",                        "outing_id":None, "created_at":"2 Mar" },
    { "id":"t2", "user_id":"u1", "delta":+1, "reason":"Hosted at Addison Road Markets",         "outing_id":"o0", "created_at":"20 Aug" },
    { "id":"t3", "user_id":"u2", "delta":+3, "reason":"Starter credits",                        "outing_id":None, "created_at":"11 Feb" },
    { "id":"t4", "user_id":"u2", "delta":-1, "reason":"Joined Cornersmith",                     "outing_id":"o1", "created_at":"21 Aug" },
    { "id":"t5", "user_id":"u3", "delta":+3, "reason":"Starter credits",                        "outing_id":None, "created_at":"30 Jan" },
    { "id":"t6", "user_id":"u4", "delta":+3, "reason":"Starter credits",                        "outing_id":None, "created_at":"18 Apr" },
    { "id":"t7", "user_id":"u4", "delta":-1, "reason":"Joined Cornersmith",                     "outing_id":"o1", "created_at":"22 Aug" }
]

conn = sqlite3.connect("events.db")
cursor = conn.cursor()

# Clear old users table, recreating it might not drop it properly
cursor.execute("DROP TABLE IF EXISTS users")
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

for u in users:
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, username, bio, gender, age_band, city, tags_followed, suspended_until, verified_at, face, noshows)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (u["id"], u["username"], u["bio"], u["gender"], u["age_band"], u["city"], json.dumps(u["tags_followed"]), u["suspended_until"], u["verified_at"], u["face"], u["noshows"]))

for p in places:
    cursor.execute("""
        INSERT OR REPLACE INTO places (id, name, address, suburb, img, plate)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (p["id"], p["name"], p["address"], p["suburb"], p["img"], p["plate"]))

for o in outings:
    cursor.execute("""
        INSERT OR REPLACE INTO outings (id, day, host_id, place_id, starts_at, seats, status, description, tags, restrict_gender, restrict_age_bands)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (o["id"], o["day"], o["host_id"], o["place_id"], o["starts_at"], o["seats"], o["status"], o["description"], json.dumps(o["tags"]), o["restrict_gender"], json.dumps(o["restrict_age_bands"])))

for r in rsvps:
    cursor.execute("""
        INSERT OR REPLACE INTO rsvps (id, outing_id, user_id, state)
        VALUES (?, ?, ?, ?)
    """, (r["id"], r["outing_id"], r["user_id"], r["state"]))

for c in comments:
    cursor.execute("""
        INSERT OR REPLACE INTO comments (id, place_id, user_id, outing_id, body, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (c["id"], c["place_id"], c["user_id"], c["outing_id"], c["body"], c["created_at"]))

for m in messages:
    cursor.execute("""
        INSERT OR REPLACE INTO messages (id, outing_id, user_id, body, at)
        VALUES (?, ?, ?, ?, ?)
    """, (m["id"], m["outing_id"], m["user_id"], m["body"], m["at"]))

for t in txns:
    cursor.execute("""
        INSERT OR REPLACE INTO txns (id, user_id, delta, reason, outing_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (t["id"], t["user_id"], t["delta"], t["reason"], t["outing_id"], t["created_at"]))

conn.commit()
conn.close()

print("Database seeded successfully.")
