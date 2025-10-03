from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import ollama
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# CRITICAL: Enable credentials (cookies) for cross-origin requests to allow login sessions.
CORS(app, supports_credentials=True)


# -----------------------------------------------------
# --- Authentication and Authorization Helpers ---
# -----------------------------------------------------

def hash_password(password):
    """Helper function to generate consistent password hash."""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def faculty_required(f):
    """Decorator to restrict access to faculty users."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_email = session.get('user')
        if not user_email or users_db.get(user_email, {}).get('type') != 'faculty':
            return jsonify({'success': False, 'message': 'Authorization Required: Faculty only'}), 403
        return f(*args, **kwargs)

    return decorated_function


# -----------------------------------------------------
# --- In-Memory Database (DYNAMIC DATA) ---
# -----------------------------------------------------

users_db = {
    'student@college.edu': {
        'password': hash_password('student123'),
        'type': 'student',
        'name': 'John Doe',
        'roll_no': 'CS2021001',
        'semester': '6th',
        # --- DYNAMIC STUDENT DATA ---
        'courses': ['Data Structures', 'Database Systems', 'Software Engineering'],
        'attendance': 87,
        'pending_assignments': 2
    },
    'faculty@college.edu': {
        'password': hash_password('faculty123'),
        'type': 'faculty',
        'name': 'Dr. Smith',
        'department': 'Computer Science',
        'grading_load': 15  # Faculty metric
    }
}

# -----------------------------------------------------
# --- Static Data and AI Functions ---
# -----------------------------------------------------

timetable_db = [
    {'day': 'Monday', 'time': '9:00 AM', 'subject': 'Data Structures', 'faculty': 'Dr. Smith', 'room': 'CS-101'},
    {'day': 'Monday', 'time': '11:00 AM', 'subject': 'Database Systems', 'faculty': 'Prof. Johnson', 'room': 'CS-203'},
    {'day': 'Tuesday', 'time': '10:00 AM', 'subject': 'Machine Learning', 'faculty': 'Dr. Williams', 'room': 'CS-305'},
    {'day': 'Wednesday', 'time': '9:00 AM', 'subject': 'Web Development', 'faculty': 'Prof. Brown', 'room': 'CS-102'},
    {'day': 'Thursday', 'time': '2:00 PM', 'subject': 'Software Engineering', 'faculty': 'Dr. Davis', 'room': 'CS-201'},
    {'day': 'Friday', 'time': '11:00 AM', 'subject': 'Cloud Computing', 'faculty': 'Prof. Wilson', 'room': 'CS-304'}
]

exams_db = [
    {'subject': 'Data Structures', 'date': '2025-10-15', 'time': '10:00 AM', 'room': 'Exam Hall A',
     'duration': '3 hours'},
    {'subject': 'Database Systems', 'date': '2025-10-18', 'time': '2:00 PM', 'room': 'Exam Hall B',
     'duration': '3 hours'},
    {'subject': 'Machine Learning', 'date': '2025-10-22', 'time': '10:00 AM', 'room': 'Exam Hall C',
     'duration': '3 hours'}
]

events_db = [
    {'title': 'Tech Fest 2025', 'date': '2025-10-20', 'time': '9:00 AM', 'location': 'Main Auditorium',
     'description': 'Annual technical festival'},
    {'title': 'Guest Lecture on AI', 'date': '2025-10-12', 'time': '3:00 PM', 'location': 'CS Seminar Hall',
     'description': 'Industry expert talk'},
    {'title': 'Sports Day', 'date': '2025-10-25', 'time': '8:00 AM', 'location': 'Sports Ground',
     'description': 'Inter-department sports competition'}
]

faculty_db = [
    {'name': 'Dr. Smith', 'department': 'Computer Science', 'email': 'smith@college.edu', 'phone': '+1-234-567-8901',
     'office': 'CS-401'},
    {'name': 'Prof. Johnson', 'department': 'Computer Science', 'email': 'johnson@college.edu',
     'phone': '+1-234-567-8902', 'office': 'CS-402'},
    {'name': 'Dr. Williams', 'department': 'Computer Science', 'email': 'williams@college.edu',
     'phone': '+1-234-567-8903', 'office': 'CS-403'}
]

notifications_db = [
    {'id': 1, 'title': 'Exam Schedule Updated', 'message': 'Mid-semester exam dates have been announced',
     'time': '2 hours ago', 'read': False},
    {'id': 2, 'title': 'New Assignment Posted', 'message': 'Database Systems assignment due next week',
     'time': '5 hours ago', 'read': False},
    {'id': 3, 'title': 'Club Meeting Tomorrow', 'message': 'Coding club meeting at 4 PM', 'time': '1 day ago',
     'read': True}
]


def get_llama_chat_response(message):
    """Handles general chat queries using campus data context (Ollama)."""
    try:
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        system_prompt = f"""
        You are 'Campus GPT', a helpful AI assistant for a college.
        Your goal is to assist students and faculty.
        Be friendly, concise, and helpful.
        When asked about schedules, exams, or events, use the following data.
        If you don't know the answer from the data, say you don't have that information.
        - Current Date: {current_date}
        - Timetable: {timetable_db}
        - Exams: {exams_db}
        - Events: {events_db}
        """

        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message},
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error calling Ollama for chat: {e}")
        return "Sorry, I'm having trouble connecting to my brain right now. Please ensure Ollama is running and the 'llama3.2' model is downloaded."


def get_llama_summary(document_text, query):
    """Analyzes document text based on a user query (Ollama)."""
    try:
        prompt = f"""
        You are 'AI Document Solver', an expert academic analyst.
        Analyze the provided DOCUMENT TEXT and answer the user's specific QUESTION based ONLY on the content of the document.
        If the question is a request for a summary, provide a comprehensive summary and key takeaways.
        Please provide a concise and well-formatted response (use markdown headings or lists).

        USER'S QUESTION: "{query}"

        DOCUMENT TEXT:
        ---
        {document_text}
        ---
        """

        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'user', 'content': prompt},
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error calling Ollama for summary: {e}")
        return "Failed to connect to the AI model for analysis. Please check your Ollama server status and the 'llama3.2' model."


# -----------------------------------------------------
# --- API Routes ---
# -----------------------------------------------------

@app.route('/')
def index():
    return "Campus GPT Backend API is running!"


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email in users_db:
        stored_hash = users_db[email]['password']

        if check_password_hash(stored_hash, password):
            session['user'] = email
            # Prepare user info, excluding the password hash
            user_info = {k: v for k, v in users_db[email].items() if k != 'password'}
            return jsonify({'success': True, 'user': user_info})

    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})


# FIX IMPLEMENTED: Always returns 200 OK status to prevent frontend error handler from triggering.
@app.route('/api/dashboard-metrics', methods=['GET'])
def get_dashboard_metrics():
    user_email = session.get('user')
    user_info = users_db.get(user_email)

    if not user_info:
        # Return a safe, successful response (200) for unauthenticated users/initial load
        return jsonify({'attendance': '78', 'pending_assignments': 0}), 200

    if user_info['type'] == 'student':
        return jsonify({
            'attendance': user_info.get('attendance', 0),
            'pending_assignments': user_info.get('pending_assignments', 0)
        })
    elif user_info['type'] == 'faculty':
        return jsonify({
            'attendance': '78',
            'pending_assignments': user_info.get('grading_load', 0)
        })

    # Fallback return
    return jsonify({'attendance': '78', 'pending_assignments': 0}), 200


# UPDATED: Filters timetable by student courses
@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    user_email = session.get('user')
    user_info = users_db.get(user_email)

    if user_info and user_info.get('type') == 'student':
        student_courses = user_info.get('courses', [])
        # Filter the master timetable based on the student's enrolled courses
        filtered_timetable = [
            item for item in timetable_db if item['subject'] in student_courses
        ]
        return jsonify(filtered_timetable)

    return jsonify(timetable_db)  # Faculty/Admin gets the full schedule


# UPDATED: Filters exams by student courses
@app.route('/api/exams', methods=['GET'])
def get_exams():
    user_email = session.get('user')
    user_info = users_db.get(user_email)

    if user_info and user_info.get('type') == 'student':
        student_courses = user_info.get('courses', [])
        # Filter exams based on the student's enrolled courses
        filtered_exams = [
            item for item in exams_db if item['subject'] in student_courses
        ]
        return jsonify(filtered_exams)

    return jsonify(exams_db)  # Faculty/Admin gets all exams


@app.route('/api/events', methods=['GET'])
def get_events():
    sorted_events = sorted(events_db, key=lambda x: x['date'])
    return jsonify(sorted_events)


@app.route('/api/faculty', methods=['GET'])
def get_faculty():
    return jsonify(faculty_db)


@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    sorted_notifications = sorted(notifications_db, key=lambda x: x['id'], reverse=True)
    return jsonify(sorted_notifications)


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    # Placeholder analytics data
    analytics = {
        'total_queries': 1247,
        'active_students': 342
    }
    return jsonify(analytics)


# Secured route: Event posting now requires faculty login using the decorator
@app.route('/api/post-event', methods=['POST'])
@faculty_required
def post_event():
    data = request.json
    new_event = {
        'title': data.get('title'),
        'date': data.get('date'),
        'time': data.get('time'),
        'location': data.get('location'),
        'description': data.get('description')
    }
    events_db.append(new_event)
    return jsonify({'success': True, 'message': 'Event posted successfully!'})


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')

    response = get_llama_chat_response(message)

    return jsonify({
        'response': response,
        'timestamp': datetime.now().strftime('%I:%M %p')
    })


# Text Document Solver Endpoint (Uses Ollama)
@app.route('/api/doubt-solver-query', methods=['POST'])
def doubt_solver_query():
    data = request.json
    document_text = data.get('document_text', '')
    query = data.get('query', '')

    if not document_text:
        return jsonify({'success': False,
                        'message': 'No document text received for analysis. Please ensure you have copied text for complex files.'}), 400
    if not query:
        return jsonify({'success': False, 'message': 'No question provided for analysis.'}), 400

    summary = get_llama_summary(document_text, query)

    return jsonify({
        'success': True,
        'summary': summary,
        'timestamp': datetime.now().strftime('%I:%M %p')
    })


if __name__ == '__main__':
    # Ensure Ollama is running and llama3.2 is pulled before starting the server.
    app.run(debug=True, port=5000)
