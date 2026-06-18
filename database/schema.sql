-- =========================
-- USERS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    role TEXT DEFAULT 'patient'

);

-- =========================
-- PATIENTS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS patients (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    age INTEGER,

    gender TEXT,

    symptoms TEXT,

    priority TEXT,

    department TEXT,

    wait_time TEXT,

    status TEXT DEFAULT 'Waiting',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)

);

-- =========================
-- DOCTORS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS doctors (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    department TEXT,

    availability TEXT

);

-- =========================
-- APPOINTMENTS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS appointments (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER,

    doctor_name TEXT NOT NULL,

    department TEXT NOT NULL,

    appointment_date TEXT,

    appointment_time TEXT NOT NULL,

    status TEXT DEFAULT 'Scheduled',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =========================
-- TRIAGE LOGS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS triage_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    symptoms TEXT NOT NULL,

    ai_response TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
        REFERENCES patients(id)

);