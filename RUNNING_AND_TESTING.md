# Running and Testing the Insider Threat Detection System

This guide provides step-by-step instructions on how to run the project locally (either with Docker or without Docker) and how to verify that the system is working correctly.

---

## 1. Running the Project

### Option A: Using Docker (Recommended)
If you have Docker and `docker-compose` installed:
1. Open a terminal in the root directory (`d:\ITD\insider-threat-system`).
2. Run the following command:
   ```bash
   docker-compose up --build
   ```
3. Docker will automatically install dependencies, build the frontend, and start all services (PostgreSQL, Redis, Backend, Frontend, and ML Worker).

### Option B: Running Locally (Without Docker)
If Docker is not available or if you encounter issues, you can run the services manually. We have configured the backend to gracefully fall back to an SQLite database and an AsyncIO in-memory queue for WebSocket alerts if Postgres/Redis are missing.

**Start the Backend:**
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd d:\ITD\insider-threat-system\backend
   ```
2. Activate the virtual environment (assuming you already ran `python -m venv venv` and `pip install -r requirements.txt`):
   ```bash
   .\venv\Scripts\activate
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

**Start the Frontend:**
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd d:\ITD\insider-threat-system\frontend
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```

---

## 2. Checking if the System Works Correctly

Once the system is up and running (Backend on port 8000, Frontend on port 3000 or 5173 depending on Vite), follow these steps to verify it works end-to-end:

### Step 1: Verify the Frontend Loads & Authentication
1. Open your browser and navigate to `http://localhost:3000` (or `http://localhost:5173` if running manually via `npm run dev`).
2. You should see the login page.
3. Log in using the default seeded credentials:
   - **Username**: `admin`
   - **Password**: `Admin123!`
4. You should be redirected to the **Security Overview Dashboard** where the UI metrics, trend charts, and high-risk user tables render correctly.

### Step 2: Verify Real-Time Alerts via WebSockets
To ensure the backend scoring pipeline and WebSockets are functioning:

1. Keep the dashboard open in your browser (it should be connected to the WebSocket).
2. Open a terminal (or PowerShell) and simulate a high-risk activity by sending a `POST` request to the backend. You will need your JWT token which you can grab from the browser's Local Storage, or you can run this PowerShell command to simulate a login and an ingest:

```powershell
# 1. Get the Token
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method Post -Body @{ username="admin"; password="Admin123!" } -ContentType "application/x-www-form-urlencoded"
$token = $response.access_token

# 2. Fire a High-Risk Event (Privilege Escalation)
$body = @{
    user_id = "00000000-0000-0000-0000-000000000000" # Replace with a valid UUID from your users table if you want it tied to a specific user, or omit user_id if you look it up dynamically. 
    # (For easier testing, pick any UUID from the /users endpoint)
    event_type = "PRIVILEGE_ESCALATION"
    resource_accessed = "admin/passwd"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/logs/ingest" -Method Post -Headers @{ Authorization="Bearer $token" } -Body $body -ContentType "application/json"
```
*(Note: To make it easier, you can also just use the Swagger UI at `http://localhost:8000/docs`, authenticate via the top right "Authorize" button, and test the `/logs/ingest` endpoint directly).*

3. **Expected Result**: Immediately after the request succeeds, you should see a red **"New High-Risk Alert"** toast slide in from the top right of your React Dashboard!

### Step 3: Check Analytics and Profiles
1. Navigate to the **Users** tab and search for a user. Click on them to view their **User Profile**.
2. Verify that their **Risk History** chart and **Baseline Profile** load.
3. Navigate to the **Alerts** tab. You should see the simulated alert from Step 2 listed there. Try clicking the "Acknowledge" button (Checkmark icon) to see it transition to "Ack'd".
4. Navigate to the **Analytics** tab and verify the bar charts, heatmaps, and trend area charts are populated with the seeded data.

---

## 3. Running Automated Tests
If you want to verify the internal backend logic:
1. Open a terminal in the `backend` directory with the virtual environment activated.
2. Run the tests:
   ```bash
   pytest tests/ -v --tb=short
   ```
3. You should see the tests pass, verifying the Auth, DB, ML, and Scoring flows.
