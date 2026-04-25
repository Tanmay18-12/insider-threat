# Insider Threat Detection System: Interview Prep Guide

This guide is designed to help you confidently explain and discuss the Insider Threat Detection System during your technical interview. It breaks down the architecture, the machine learning logic, the real-time alerting pipeline, and the design decisions.

---

## 1. Executive Summary: What is it?
The **Insider Threat Detection System** is a full-stack, AI-powered cybersecurity platform. Its primary purpose is to continuously monitor user activity logs (e.g., file access, logins, privilege escalations) and automatically detect anomalous or malicious behavior indicating an "insider threat" (an employee or compromised account doing something they shouldn't).

**Why is it valuable?**
Traditional rule-based security systems catch known bad actions (e.g., "Alert if an IP is from Russia"). This system uses **Machine Learning (ML)** to establish a baseline of "normal" behavior for every individual user and flags deviations from that baseline, catching zero-day threats or sophisticated lateral movements that rules would miss.

---

## 2. The Tech Stack & Architecture
Be prepared to talk about why you chose these technologies. The stack was chosen for high performance, modern developer experience, and scalability.

### **Frontend (The Dashboard)**
*   **React 18 & Vite**: Lightning-fast build times and modern component architecture.
*   **Tailwind CSS (v4)**: Utility-first CSS for building a highly aesthetic, responsive, and custom dark-mode UI without bloated stylesheets.
*   **Zustand**: Lightweight, boilerplate-free state management used for handling authentication state and live alert queues.
*   **Recharts**: Used to render the complex risk history trend lines and analytics charts.
*   **WebSockets**: Maintains a persistent connection to the backend to instantly push new security alerts to the UI.

### **Backend (The Engine)**
*   **Python & FastAPI**: Chosen over Django/Flask because of its asynchronous capabilities, exceptional speed, and native WebSocket support.
*   **SQLAlchemy (SQLite / PostgreSQL)**: An ORM that allows the system to easily run locally via SQLite, but is fully compatible with a heavy-duty PostgreSQL database in production.
*   **Scikit-Learn (Machine Learning)**: The industry standard for classical ML. Used to build the anomaly detection engine.
*   **Redis (Pub/Sub) / AsyncIO Queues**: Used as a message broker. When the ML engine flags a critical event, it publishes an alert to a queue, which is then instantly broadcasted to all connected frontend clients.

---

## 3. How It Works: The Core Workflows

If an interviewer asks, *"Walk me through what happens when a user downloads a sensitive file at 3 AM"*, here is your answer:

### **Phase 1: Ingestion & Feature Engineering**
1. An activity log arrives at the backend API (`POST /logs/ingest`).
2. The `ScoringService` takes the raw log (timestamp, event type, metadata) and runs **Feature Engineering**. 
3. It converts the timestamp into actionable features: *Is it off-hours? Is it a weekend?* It also checks the metadata: *Did they download 1 file or 500 files?*

### **Phase 2: Machine Learning Evaluation**
The system uses a **Hybrid Ensemble Approach** to evaluate the risk score.
1. **Isolation Forest (Unsupervised)**: This algorithm looks at the user's historical baseline profile. It isolates the new activity and determines how "abnormal" it is compared to what this specific user usually does.
2. **Gradient Boosting (Supervised)**: This algorithm is trained on past labeled data (known anomalies vs. known normal logs). It predicts the probability that the event is inherently malicious (e.g., privilege escalation is universally bad, regardless of the user's baseline).
3. The system blends the output of both models to produce a final `risk_score` from 0 to 100.

### **Phase 3: Real-Time Alerting**
1. If the `risk_score` exceeds the threshold (e.g., 75), the system flags the log as `is_anomalous=True`.
2. It immediately writes an `Alert` record to the database.
3. It publishes a message to the internal **Alert Queue** (or Redis Pub/Sub).
4. The FastAPI WebSocket manager picks up the message and pushes it to the React frontend.
5. The frontend receives the socket message and immediately triggers a red toast notification on the user's screen.

---

## 4. Key Design Decisions to Highlight

Interviewers love when you can justify your architectural decisions.

*   **Why WebSockets over Polling?** 
    *   *Your Answer:* "Security dashboards require real-time visibility. Having the React app poll the API every 5 seconds would hammer the database and create unnecessary network overhead. WebSockets allow the server to push alerts only when an anomaly occurs, saving resources and reducing latency."
*   **Why a Hybrid ML Approach?** 
    *   *Your Answer:* "Unsupervised learning (Isolation Forest) is great for catching new, unknown deviations, but it can be noisy. Supervised learning (Gradient Boosting) is highly accurate for known threat patterns but misses zero-day behaviors. By combining them, we get the best of both worlds: catching behavioral deviations while heavily penalizing inherently dangerous actions."
*   **Why Zustand over Redux?**
    *   *Your Answer:* "Redux is powerful but introduces a lot of boilerplate. For this application, global state was primarily needed just to hold the JWT authentication token and the ephemeral real-time alert stack. Zustand provided a much cleaner, hook-based API without the overhead."

---

## 5. Potential Interview Questions & Answers

**Q: How do you handle cold-start problems for the Machine Learning model?**
> **A:** "When a new user joins the system, the Isolation Forest doesn't have enough historical data to build a reliable baseline, which could lead to false positives. To mitigate this, the system relies more heavily on the supervised Gradient Boosting model and static heuristics during the user's first few weeks until enough data is collected to re-train their specific baseline."

**Q: How is the system deployed and scaled?**
> **A:** "The entire platform is fully containerized using Docker and Docker Compose. The backend, frontend, and database are segregated into their own containers. To scale this, we could deploy the containers to a Kubernetes cluster, swap the local SQLite database for a managed PostgreSQL instance (like AWS RDS), and use a managed Redis cluster to handle Pub/Sub across multiple scaled instances of the FastAPI backend."

**Q: What happens if the WebSocket connection drops?**
> **A:** "The frontend uses a custom `useWebSocket` React hook that automatically attempts to reconnect using an exponential backoff strategy if the connection drops. Furthermore, because all alerts are persisted to the PostgreSQL/SQLite database *before* they are broadcasted, no data is ever lost. The frontend fetches the latest state via standard REST endpoints on initial load."
