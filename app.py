from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, Response, session
)
from datetime import date
import csv
import iopy

from database import (
    initialize_database,
    add_subject,
    get_all_subjects,
    clear_subjects,
    update_subject,
    delete_subject
)

from scheduler import generate_timetable

app = Flask(__name__)
app.secret_key = "smart-exam-development-key"

DEPARTMENTS = [
    "CSE CORE", "AIDS", "AIML", "IT",
    "ECE", "EEE", "BIOTECHNOLOGY"
]

YEARS = ["Year 1", "Year 2", "Year 3", "Year 4"]
SEMESTERS = ["Semester 1", "Semester 2"]
SESSIONS = ["Morning", "Afternoon"]

initialize_database()


@app.route("/", methods=["GET", "POST"])
def home():
    timetable = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            subject = {
                "name": request.form.get("subject", "").strip(),
                "year": request.form.get("year", ""),
                "semester": request.form.get("semester", ""),
                "department": request.form.get("department", ""),
                "date": request.form.get("examDate", ""),
                "session": request.form.get("session", "")
            }

            if not subject["name"]:
                flash("Enter a subject name.", "error")

            elif subject["year"] not in YEARS:
                flash("Select a valid academic year.", "error")

            elif subject["semester"] not in SEMESTERS:
                flash("Select a valid semester.", "error")

            elif subject["department"] not in DEPARTMENTS:
                flash("Select a valid department.", "error")

            elif subject["session"] not in SESSIONS:
                flash("Select a valid exam session.", "error")

            elif not subject["date"]:
                flash("Select an earliest exam date.", "error")

            elif subject["date"] < date.today().isoformat():
                flash("Choose today or a future date.", "error")

            else:
                try:
                    date.fromisoformat(subject["date"])
                    add_subject(subject)
                    session["timetable_generated"] = False
                    flash("Subject saved to the database!", "success")
                except ValueError:
                    flash("Enter a valid date.", "error")

        elif action == "generate":
            subjects = get_all_subjects()

            if not subjects:
                    flash("Add at least one subject first.", "error")
                    session["timetable_generated"] = False
            else:
                    session["timetable_generated"] = True
                    flash("Timetable generated successfully!", "success")

        elif action == "clear":
            clear_subjects()
            session["timetable_generated"] = False
            flash("All saved subjects have been cleared.", "success")

        return redirect(url_for("home"))

    subjects = get_all_subjects()

    if session.get("timetable_generated") and subjects:
        timetable = generate_timetable(subjects)
    else:
        timetable = []

    return render_template(
        "index.html",
        subjects=subjects,
        timetable=timetable,
        departments=DEPARTMENTS,
        years=YEARS,
        semesters=SEMESTERS,
        today=date.today().isoformat()
    )

@app.route("/edit/<int:subject_id>", methods=["POST"])
def edit_subject(subject_id):
    existing = next(
        (s for s in get_all_subjects() if s["id"] == subject_id),
        None
    )

    if existing is None:
        flash("Subject not found.", "error")
        return redirect(url_for("home"))

    subject = {
        "name": request.form.get("subject", "").strip(),
        "year": request.form.get("year", ""),
        "semester": request.form.get("semester", ""),
        "department": request.form.get("department", ""),
        "date": request.form.get("examDate", ""),
        "session": request.form.get("session", "")
    }

    if (
        not subject["name"]
        or subject["year"] not in YEARS
        or subject["semester"] not in SEMESTERS
        or subject["department"] not in DEPARTMENTS
        or subject["session"] not in SESSIONS
    ):
        flash("Please enter valid subject details.", "error")
        return redirect(url_for("home"))

    try:
        chosen_date = date.fromisoformat(subject["date"])
        if chosen_date < date.today():
            flash("Choose today or a future date.", "error")
            return redirect(url_for("home"))
    except ValueError:
        flash("Enter a valid exam date.", "error")
        return redirect(url_for("home"))

    update_subject(subject_id, subject)
    flash("Subject updated successfully!", "success")
    return redirect(url_for("home"))


@app.route("/delete/<int:subject_id>", methods=["POST"])
def remove_subject(subject_id):
    delete_subject(subject_id)
    flash("Subject deleted successfully!", "success")
    return redirect(url_for("home"))

@app.route("/download")
def download():
    subjects = get_all_subjects()

    if not subjects:
        flash("Add subjects before downloading.", "error")
        return redirect(url_for("home"))

    timetable = generate_timetable(subjects)

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "date", "session", "year",
            "semester", "department", "name"
        ]
    )
    writer.writeheader()

    for exam in timetable:
        writer.writerow({
            key: exam[key]
            for key in writer.fieldnames
        })

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=timetable.csv"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)