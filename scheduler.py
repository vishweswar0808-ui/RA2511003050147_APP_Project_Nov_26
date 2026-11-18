from datetime import date, timedelta


def generate_timetable(subjects):
    """
    Generate an exam timetable from a list of subjects.

    Each subject must contain:
    name, year, semester, department, date, session.
    The date is the earliest allowed exam date.
    """

    scheduled = []

    ordered_subjects = sorted(
        subjects,
        key=lambda item: item["date"]
    )

    for subject in ordered_subjects:
        exam_date = date.fromisoformat(subject["date"])
        exam = subject.copy()
        exam["session"] = exam.get("session", "Morning")

        while True:
            conflict = False

            for existing in scheduled:
                same_date = existing["date"] == exam_date.isoformat()

                if not same_date:
                    continue

                same_year = existing["year"] == exam["year"]

                same_subject = (
                    existing["name"].strip().casefold()
                    == exam["name"].strip().casefold()
                )

                different_department = (
                    existing["department"] != exam["department"]
                )

                # Same subject + same year + different departments
                # must be scheduled on different dates.
                if (
                    same_year
                    and same_subject
                    and different_department
                ):
                    conflict = True
                    break

                # Avoid two exams for the same department,
                # academic year and semester on the same date.
                same_cohort = (
                    existing["department"] == exam["department"]
                    and existing["year"] == exam["year"]
                    and existing["semester"] == exam["semester"]
                )

                if same_cohort:
                    conflict = True
                    break

            if not conflict:
                exam["date"] = exam_date.isoformat()
                scheduled.append(exam)
                break

            exam_date += timedelta(days=1)

    return sorted(
        scheduled,
        key=lambda item: (item["date"], item["session"])
    )