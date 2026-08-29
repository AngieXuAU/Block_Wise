# Block_Wise

Connecting tourists and locals through small-group authentic experiences with vibe filters, introvert-friendly capacity caps, and interactive map integrations.

## How to Run the Website

You need to run two things: the **Backend** and the **Frontend**, in two separate terminal windows.

### Step 1: Start the Backend (Terminal 1)
Open a terminal and run these commands to start the backend on port `8000`:
```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```

### Step 2: Start the Frontend (Terminal 2)
Open a **new** terminal in the main folder (`Block_Wise`) and run this command to start the frontend on port `8080` (this must be different from 8000!):
```bash
python -m http.server 8080
```

### Step 3: Open the Website
Click here or type this into your browser: 
👉 [http://127.0.0.1:8080/blockwise-v2_1.html](http://127.0.0.1:8080/blockwise-v2_1.html)

---

### Backend API Documentation
If you ever need to look at the backend API documentation, you can view it here while the backend is running:
* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## How to Check the Connection is Working

To verify that the frontend is successfully talking to your backend database, follow these simple steps:

1. **Verify Initial Data Load**:
   - Open the frontend website. If you see upcoming outings (like "Matcha Cafe" or "Coastal Walk") in the feed, it means the frontend successfully downloaded the data from the backend! If it's a blank screen or empty, the backend might not be running.

2. **Test Creating Data**:
   - Click the **HOST ONE** button at the top of the website.
   - Fill in some dummy details for an outing and click **Post outing**.
   - If the new outing instantly shows up on the feed, your frontend successfully sent data to the backend.

3. **Check the Backend Logs**:
   - Look at the terminal running the **Backend** (Terminal 1).
   - You should see logs like `GET /api/state 200 OK` or `POST /api/outings 201 Created` appearing every time you interact with the website. This is the definitive proof they are talking!

---

## How to Reset the Database

If you have added a bunch of test data and want to wipe it all away to return to the clean, base demo database, follow these steps:

1. Stop your backend server in Terminal 1 (press `Ctrl+C`).
2. Delete the `events.db` file located in the `server` folder.
3. Run the seed script to generate a fresh database:
   ```bash
   cd server
   python seed_db.py
   ```
4. Restart your backend server (`uvicorn main:app --reload`). Refresh your browser, and you're back to a clean slate!
