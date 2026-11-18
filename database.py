import sqlite3

DATABASE = "exam_timetable.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                year TEXT NOT NULL,
                semester TEXT NOT NULL,
                department TEXT NOT NULL,
                exam_date TEXT NOT NULL,
                session TEXT NOT NULL
            )
        """)


def add_subject(subject):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO subjects
            (name, year, semester, department, exam_date, session)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            subject["name"],
            subject["year"],
            subject["semester"],
            subject["department"],
            subject["date"],
            subject["session"]
        ))


def get_all_subjects():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, name, year, semester, department,
                   exam_date, session
            FROM subjects
            ORDER BY id
        """).fetchall()

    return [
        {
            "id": row["id"],
            "name": row["name"],
            "year": row["year"],
            "semester": row["semester"],
            "department": row["department"],
            "date": row["exam_date"],
            "session": row["session"]
        }
        for row in rows
    ]


def clear_subjects():
    with get_connection() as connection:
        connection.execute("DELETE FROM subjects")


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")
def update_subject(subject_id, subject):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE subjects
            SET name = ?,
                year = ?,
                semester = ?,
                department = ?,
                exam_date = ?,
                session = ?
            WHERE id = ?
            """,
            (
                subject["name"],
                subject["year"],
                subject["semester"],
                subject["department"],
                subject["date"],
                subject["session"],
                subject_id
            )
        )
        connection.commit()
    finally:
        connection.close()


def delete_subject(subject_id):
    connection = get_connection()

    try:
        connection.execute(
            "DELETE FROM subjects WHERE id = ?",
            (subject_id,)
        )
        connection.commit()
    finally:
        connection.close()
def update_subject(subject_id, subject):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE subjects
            SET name = ?,
                year = ?,
                semester = ?,
                department = ?,
                exam_date = ?,
                session = ?
            WHERE id = ?
            """,
            (
                subject["name"],
                subject["year"],
                subject["semester"],
                subject["department"],
                subject["date"],
                subject["session"],
                subject_id
            )
        )


def delete_subject(subject_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM subjects WHERE id = ?",
            (subject_id,)
        )