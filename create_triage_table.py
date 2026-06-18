import sqlite3

conn = sqlite3.connect(
    "database/hospital.db"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS triage_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER,

    symptoms TEXT NOT NULL,

    ai_response TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
    REFERENCES patients(id)

)
""")

conn.commit()

conn.close()

print(
    "triage_logs table created successfully!"
)