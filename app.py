from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import os
import sqlite3
import bcrypt

from dotenv import load_dotenv

from services.gemini_service import analyze_symptoms

from services.triage_service import (
    classify_urgency,
    assign_department,
    calculate_priority_score,
    estimate_wait_time
)

from services.queue_service import (
    queue_position,
    queue_recommendation
)

# ------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ------------------------------------

load_dotenv()

# ------------------------------------
# FLASK APP
# ------------------------------------

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "mediflow_secret_key"
)

# ------------------------------------
# DATABASE CONFIG
# ------------------------------------

DB_PATH = "database/hospital.db"

# ------------------------------------
# DATABASE CONNECTION
# ------------------------------------

def get_db():

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn

# ------------------------------------
# DATABASE INITIALIZATION
# ------------------------------------

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    with open(
        "database/schema.sql",
        "r",
        encoding="utf-8"
    ) as file:
        cursor.executescript(file.read())

    conn.commit()
    conn.close()


# ------------------------------------
# AUTH HELPER
# ------------------------------------

def is_logged_in():
    return "user_id" in session


# ------------------------------------
# HOME PAGE
# ------------------------------------

@app.route("/")
def home():
    return render_template(
        "index.html"
    )


# ------------------------------------
# HEALTH CHECK
# ------------------------------------

@app.route("/health")
def health():
    return {
        "status": "running",
        "application": "MediFlow AI"
    }


# =====================================
# REGISTER
# =====================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        existing_user = cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:

            conn.close()

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password
            )
            VALUES
            (
                ?,
                ?,
                ?
            )
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =====================================
# LOGIN
# =====================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        user = cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        if user:

            stored_password = user["password"]

            if bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8")
            ):

                session["user_id"] = user["id"]
                session["name"] = user["name"]
                session["role"] = user["role"]

                flash(
                    "Login successful.",
                    "success"
                )

                return redirect(
                    url_for(
                        "patient_dashboard"
                    )
                )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "info"
    )

    return redirect(
        url_for("home")
    )


# =====================================
# PROTECTED ROUTE CHECK
# =====================================

def require_login():

    if not is_logged_in():

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("login")
        )

    return None


# =====================================
# PATIENT DASHBOARD
# =====================================

@app.route("/patient-dashboard")
def patient_dashboard():

    auth_check = require_login()

    if auth_check:
        return auth_check

    conn = get_db()
    cursor = conn.cursor()

    # Latest AI Triage

    cursor.execute(
        """
        SELECT
            symptoms,
            priority,
            department,
            wait_time
        FROM patients
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    )

    triage = cursor.fetchone()

    # Queue Position

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM patients
        WHERE status = 'Waiting'
        """
    )

    queue_position = cursor.fetchone()[0]

    # Active Appointments Only

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM appointments
        WHERE patient_id = ?
        AND status = 'Scheduled'
        """,
        (session["user_id"],)
    )

    appointment_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "patient_dashboard.html",
        name=session["name"],
        triage=triage,
        queue_position=queue_position,
        appointment_count=appointment_count
    )

# =====================================
# book-appointment
# =====================================


@app.route(
    "/book-appointment",
    methods=["POST"]
)
def book_appointment():

    auth_check = require_login()

    if auth_check:
        return auth_check

    doctor = request.form["doctor"]
    department = request.form["department"]
    time_slot = request.form["time"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO appointments
        (
            patient_id,
            doctor_name,
            department,
            appointment_time
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            session["user_id"],
            doctor,
            department,
            time_slot
        )
    )

    conn.commit()
    conn.close()

    return redirect("/appointments")

# =====================================
# My-appointment
# =====================================


@app.route("/my-appointments")
def my_appointments():

    auth_check = require_login()

    if auth_check:
        return auth_check

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            doctor_name,
            department,
            appointment_time,
            status
        FROM appointments
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    )

    appointments = cursor.fetchall()

    conn.close()

    return render_template(
        "my_appointments.html",
        appointments=appointments
    )
# =====================================
# Cancel appointment
# =====================================


@app.route(
    "/cancel-appointment/<int:appointment_id>"
)
def cancel_appointment(appointment_id):

    auth_check = require_login()

    if auth_check:
        return auth_check

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE appointments
        SET status = 'Cancelled'
        WHERE id = ?
        """,
        (appointment_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/my-appointments")
# =====================================
# DOCTOR DASHBOARD
# =====================================

@app.route("/doctor-dashboard")
def doctor_dashboard():

    auth_check = require_login()

    if auth_check:
        return auth_check

    return render_template(
        "doctor_dashboard.html"
    )


# =====================================
# ADMIN DASHBOARD
# =====================================

@app.route("/admin-dashboard")
def admin_dashboard():

    auth_check = require_login()

    if auth_check:
        return auth_check

    conn = get_db()
    cursor = conn.cursor()

    # Total Patients

    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
    """)

    total_patients = cursor.fetchone()[0]

    # Critical Cases

    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE priority = 'Critical'
    """)

    critical_cases = cursor.fetchone()[0]

    # Doctors

    cursor.execute("""
        SELECT COUNT(*)
        FROM doctors
    """)

    total_doctors = cursor.fetchone()[0]

    # AI Analyses

    cursor.execute("""
        SELECT COUNT(*)
        FROM triage_logs
    """)

    total_triage = cursor.fetchone()[0]

    # Queue Status

    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE priority = 'Critical'
        AND status = 'Waiting'
    """)

    critical_queue = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE priority = 'High'
        AND status = 'Waiting'
    """)

    high_queue = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE priority IN ('Medium', 'Low')
        AND status = 'Waiting'
    """)

    normal_queue = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_patients=total_patients,
        critical_cases=critical_cases,
        total_doctors=total_doctors,
        total_triage=total_triage,
        critical_queue=critical_queue,
        high_queue=high_queue,
        normal_queue=normal_queue
    )


# =====================================
# APPOINTMENTS
# =====================================

@app.route("/appointments")
def appointments():

    auth_check = require_login()

    if auth_check:
        return auth_check

    return render_template(
        "appointments.html"
    )


# =====================================
# ANALYTICS
# =====================================

@app.route("/analytics")
def analytics():

    auth_check = require_login()

    if auth_check:
        return auth_check

    conn = get_db()
    cursor = conn.cursor()

    total_patients = cursor.execute(
        """
        SELECT COUNT(*)
        FROM patients
        """
    ).fetchone()[0]

    total_triage = cursor.execute(
        """
        SELECT COUNT(*)
        FROM triage_logs
        """
    ).fetchone()[0]

    critical_cases = cursor.execute(
        """
        SELECT COUNT(*)
        FROM patients
        WHERE priority='Critical'
        """
    ).fetchone()[0]

    conn.close()

    return render_template(
        "analytics.html",
        total_patients=total_patients,
        total_triage=total_triage,
        critical_cases=critical_cases
    )


# =====================================
# AI SYMPTOM ANALYSIS
# =====================================

@app.route(
    "/symptom-chat",
    methods=["GET", "POST"]
)
def symptom_chat():

    auth_check = require_login()

    if auth_check:
        return auth_check

    if request.method == "POST":

        symptoms = request.form.get(
            "symptoms",
            ""
        ).strip()

        # -------------------------
        # Default Local Analysis
        # -------------------------

        urgency = classify_urgency(
            symptoms
        )

        department = assign_department(
            symptoms
        )

        priority_score = calculate_priority_score(
            urgency
        )

        wait_time = estimate_wait_time(
            urgency
        )

        explanation = ""

        # -------------------------
        # Gemini Analysis
        # -------------------------

        try:

            ai_result = analyze_symptoms(
                symptoms
            )

            if isinstance(
                ai_result,
                dict
            ):

                urgency = ai_result.get(
                    "urgency",
                    urgency
                )

                department = ai_result.get(
                    "department",
                    department
                )

                priority_score = ai_result.get(
                    "priority_score",
                    priority_score
                )

                wait_time = ai_result.get(
                    "estimated_wait",
                    wait_time
                )

                explanation = ai_result.get(
                    "explanation",
                    ""
                )

        except Exception as e:

            print(
                "Gemini Error:",
                str(e)
            )

        # -------------------------
        # Clean Priority Score
        # -------------------------

        try:

            if isinstance(
                priority_score,
                str
            ):

                priority_score = (
                    priority_score
                    .replace(
                        "/100",
                        ""
                    )
                    .strip()
                )

            priority_score = int(
                priority_score
            )

        except:

            priority_score = calculate_priority_score(
                urgency
            )

        # -------------------------
        # Force Score Consistency
        # -------------------------

        if urgency == "Critical":

            priority_score = max(
                priority_score,
                95
            )

        elif urgency == "High":

            priority_score = max(
                priority_score,
                80
            )

        elif urgency == "Medium":

            priority_score = max(
                priority_score,
                55
            )

        elif urgency == "Low":

            priority_score = min(
                priority_score,
                30
            )

        # -------------------------
        # Save to Database
        # -------------------------

        conn = None

        try:

            conn = get_db()

            cursor = conn.cursor()

            # Save patient

            cursor.execute(
                """
                INSERT INTO patients
                (
                    user_id,
                    symptoms,
                    priority,
                    department,
                    wait_time
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    symptoms,
                    urgency,
                    department,
                    wait_time
                )
            )

            patient_id = cursor.lastrowid

            # Save AI log (optional)

            try:

                cursor.execute(
                    """
                    INSERT INTO triage_logs
                    (
                        patient_id,
                        symptoms,
                        ai_response
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        patient_id,
                        symptoms,
                        explanation
                    )
                )

            except Exception as e:

                print(
                    "triage_logs Error:",
                    str(e)
                )

            conn.commit()

        except Exception as e:

            print(
                "Database Error:",
                str(e)
            )

            if conn:
                conn.rollback()

        finally:

            if conn:
                conn.close()

        # -------------------------
        # Show Result Page
        # -------------------------

        return render_template(
            "triage_result.html",
            urgency=urgency,
            department=department,
            priority_score=priority_score,
            wait_time=wait_time,
            explanation=explanation,
            symptoms=symptoms
        )

    return render_template(
        "symptom_chat.html"
    )
# =====================================
# QUEUE STATUS
# =====================================

@app.route("/queue-status")
def queue_status_view():

    auth_check = require_login()

    if auth_check:
        return auth_check

    conn = get_db()
    cursor = conn.cursor()

    latest_patient = cursor.execute(
        """
        SELECT *
        FROM patients
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            session["user_id"],
        )
    ).fetchone()

    conn.close()

    if latest_patient:

        priority = latest_patient[
            "priority"
        ]

        department = latest_patient[
            "department"
        ]

        position = queue_position(
            priority
        )

        wait_time = (
            estimate_wait_time(
                priority
            )
        )

        recommendation = (
            queue_recommendation(
                priority
            )
        )

    else:

        priority = "Low"
        department = "General Medicine"

        position = 10

        wait_time = "30 Minutes"

        recommendation = (
            "No active triage found."
        )

    return render_template(
        "queue_status.html",
        queue_position=position,
        priority=priority,
        wait_time=wait_time,
        department=department,
        recommendation=recommendation
    )


# =====================================
# ERROR HANDLERS
# =====================================

@app.errorhandler(404)
def page_not_found(error):

    return (
        render_template(
            "index.html"
        ),
        404
    )


@app.errorhandler(500)
def internal_error(error):

    return (
        """
        <h1>
        Internal Server Error
        </h1>
        """,
        500
    )

# =====================================
# admin-patients
# =====================================

@app.route("/admin-patients")
def admin_patients():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            symptoms,
            priority,
            department,
            wait_time,
            status
        FROM patients
        ORDER BY id DESC
    """)

    patients = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_patients.html",
        patients=patients
    )

# =====================================
# admin_appointments
# =====================================

@app.route("/admin-appointments")
def admin_appointments():

    auth_check = require_login()

    if auth_check:
        return auth_check

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            doctor_name,
            department,
            appointment_time,
            status
        FROM appointments
        ORDER BY id DESC
    """)

    appointments = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_appointments.html",
        appointments=appointments
    )
# =====================================
# START APPLICATION
# =====================================

#if __name__ == "__main__":

#    try:

#        os.makedirs(
#            "database",
#            exist_ok=True
#        )

#        init_db()

#       print(
 #           "✅ Database initialized successfully"
 #       )

 #   except Exception as e:

#        print(
#            f"❌ Database initialization failed: {e}"
 #       )

  #  app.run(
 #      host="0.0.0.0",
   #     port=int(os.environ.get("PORT", 5001))
        
  #  )

# ------------------------------------
# DATABASE INITIALIZATION
# ------------------------------------

try:

    os.makedirs(
        "database",
        exist_ok=True
    )

    init_db()

    print(
        "✅ Database initialized successfully"
    )

except Exception as e:

    print(
        f"❌ Database initialization failed: {e}"
    )

# ------------------------------------
# RUN APP
# ------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5001))
    )
