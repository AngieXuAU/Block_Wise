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
