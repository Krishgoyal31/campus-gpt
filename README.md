Just LPU Things: Academic Assistant (Frontend Simulation)
⚠️ Important Notice: Simulation Mode Only
This repository is currently deployed as a fully client-side simulation using only HTML, CSS, and JavaScript.

The code you see running live (e.g., on GitHub Pages) DOES NOT make any external API calls, connect to a database (like Firestore), or utilize the LLM or Vision models (Gemini/Llama).

All interactions—including login, dashboard metrics, AI chat responses, and doubt solver analyses—are handled using hardcoded dummy data and static logic for demonstration purposes.

🎯 Project Overview
Just LPU Things is a unified academic assistant designed to centralize critical campus information (timetable, assignments, exams, faculty directory) and provide powerful AI tools for student support.

Key Simulated Features:
Role-Based Views and Security: Supports two distinct roles (Student / Faculty) using mock credentials. The interface dynamically changes:

Student: Sees Attendance and Pending Assignments.

Faculty: Sees Grading Workload, Academic Analytics, and the Admin Panel for event posting.

AI Chat Assistant Simulation: Provides interactive mock responses about personalized academic data (schedule, exams, pending tasks) based on user role.

AI Doubt Solver Simulation (Multi-Modal Demo): Features a dedicated page that simulates context-aware analysis for different file types (TXT, PDF, and Image/Vision tasks).

Dynamic Dashboard: The Home page dynamically filters the full Timetable data to show only Today's Schedule and provides quick access to metrics like attendance and upcoming tasks.

Comprehensive Academic Hub: Dedicated modules for Timetable, Exam Schedule, Pending Tasks (Assignments/Grading Load), Campus Events, and a Faculty Directory.

Modern, Responsive UI/UX: Features a sleek Dark and Light Theme toggle, full mobile responsiveness, persistent navigation search/filtering, and custom notification toast messages.

Administrative Functions: Faculty users can access a simulated Admin Panel to view analytics and Post New Events, demonstrating basic data management UI.

💻 Running the Full Web App (Integrating main.py Backend)
If you wish to run the complete, fully functional application, you must use the original Flask backend file (main.py) which contains the logic for authentication, data management, and Gemini API/Ollama LLM integration.

This step requires Python, Flask, and the necessary API keys.

1. Backend Setup
Ensure Python is installed.

Install Flask and required libraries (like google-genai for Gemini and requests for Ollama/backend interaction):

pip install Flask google-genai requests
# You may also need python-dotenv for environment variables

Set Environment Variables: Your main.py file likely requires environment variables, particularly your Gemini API key. Create a .env file in the same directory as main.py and add your key:

GEMINI_API_KEY="YOUR_API_KEY_HERE"

Run the Flask Backend:

python main.py

This will typically start the backend server on http://127.0.0.1:5000.

2. Frontend Re-integration
The client-side HTML file needs to be reverted to point to the local Flask server endpoints.

Open the HTML file and locate the DOMContentLoaded listener block in the JavaScript section.

Re-enable the API endpoint: Uncomment or restore the original API base URL that points to your Flask server (assuming it was http://127.0.0.1:5000):

// BEFORE RE-INTEGRATION (Simulation):
// const API_BASE = '[http://127.0.0.1:5000/api](http://127.0.0.1:5000/api)'; // Removed for simulation

// AFTER RE-INTEGRATION:
const API_BASE = '[http://127.0.0.1:5000/api](http://127.0.0.1:5000/api)';
// Ensure the Flask backend is running on port 5000.

Note: The frontend code you uploaded used the apiCall wrapper function to interact with the backend, which will now function correctly when pointed back to the running Flask server.

3. Usage
After running the backend and opening the modified HTML file in your browser, the application will be fully functional, including real-time AI responses and backend data management.
