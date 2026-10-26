import os
from io import BytesIO, StringIO
from flask import Flask, render_template, request, jsonify, send_file
import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "student_placement_db"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

def fetch_data():
    conn = get_connection()
    try:
        students = pd.read_sql("""
            SELECT s.student_id, s.roll_no, s.department, s.graduation_year,
                   s.eligible, s.placement_status, p.company, p.role,
                   p.package_lpa, p.placement_date
            FROM students s LEFT JOIN placements p ON s.student_id = p.student_id
        """, conn)
        skills = pd.read_sql("""
            SELECT ss.student_id, sk.skill_name
            FROM student_skills ss JOIN skills sk ON ss.skill_id = sk.skill_id
        """, conn)
        return students, skills
    finally:
        conn.close()

def analyze(students, skills):
    total = int(len(students))
    eligible_count = int(students["eligible"].fillna(0).astype(int).sum())
    placed = students[students["placement_status"] == "Placed"]
    placed_count = int(len(placed))
    rate = round(placed_count / eligible_count * 100, 2) if eligible_count else 0.0
    packages = pd.to_numeric(placed["package_lpa"], errors="coerce").dropna()
    dept = students.groupby("department", dropna=False).agg(
        students=("student_id", "count"),
        eligible=("eligible", "sum"),
        placed=("placement_status", lambda s: int((s == "Placed").sum()))
    ).reset_index()
    dept["placement_rate"] = np.where(dept["eligible"] > 0, (dept["placed"] / dept["eligible"] * 100).round(2), 0)
    skill_report = skills.groupby("skill_name").agg(student_count=("student_id", "nunique")).reset_index()
    skill_report = skill_report.sort_values("student_count", ascending=False)
    return {
        "total": total, "eligible": eligible_count, "placed": placed_count, "rate": rate,
        "avg_package": round(float(packages.mean()), 2) if len(packages) else 0,
        "median_package": round(float(packages.median()), 2) if len(packages) else 0,
        "highest_package": round(float(packages.max()), 2) if len(packages) else 0,
        "department": dept.to_dict(orient="records"),
        "skills": skill_report.head(10).to_dict(orient="records"),
        "companies": int(placed["company"].nunique()) if "company" in placed else 0
    }

def create_charts(students, skills):
    os.makedirs("reports", exist_ok=True)
    # Chart 1: department placement rate
    dept = students.groupby("department").agg(eligible=("eligible","sum"),
        placed=("placement_status", lambda s: (s == "Placed").sum())).reset_index()
    dept["rate"] = np.where(dept["eligible"] > 0, dept["placed"] / dept["eligible"] * 100, 0)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(dept["department"], dept["rate"])
    ax.set_title("Placement Rate by Department")
    ax.set_xlabel("Department"); ax.set_ylabel("Placement rate (%)")
    ax.set_ylim(0, 100); ax.grid(axis="y", alpha=.25)
    fig.tight_layout(); fig.savefig("reports/department_placement_rate.png", dpi=150); plt.close(fig)

    placed = students[students["placement_status"] == "Placed"].copy()
    packages = pd.to_numeric(placed["package_lpa"], errors="coerce").dropna()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if len(packages):
        ax.hist(packages, bins=12, edgecolor="black")
    ax.set_title("Package Distribution of Placed Students")
    ax.set_xlabel("Package (LPA)"); ax.set_ylabel("Number of students")
    ax.grid(axis="y", alpha=.25)
    fig.tight_layout(); fig.savefig("reports/package_distribution.png", dpi=150); plt.close(fig)

    skill_report = skills.groupby("skill_name")["student_id"].nunique().sort_values(ascending=False).head(10).sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(skill_report.index, skill_report.values)
    ax.set_title("Top 10 Skills Across Student Profiles")
    ax.set_xlabel("Students listing skill (count)"); ax.set_ylabel("Skill")
    ax.grid(axis="x", alpha=.25)
    fig.tight_layout(); fig.savefig("reports/top_skills.png", dpi=150); plt.close(fig)

@app.route("/")
def index():
    # Keep the landing page simple: users choose a section before seeing detailed data.
    return render_template("index.html")

@app.route("/section/<section_name>")
def section_detail(section_name):
    allowed_sections = {
        "overview": "Placement Overview",
        "departments": "Department Analysis",
        "packages": "Package Analysis",
        "skills": "Skill Demand",
        "students": "Student Records",
        "reports": "Charts & Reports",
    }
    if section_name not in allowed_sections:
        return render_template("detail.html", error="Section not found", section_name="Not found",
                               section_key="", stats=None, recent=[], departments=[], skills=[]), 404
    try:
        students, skills = fetch_data()
        stats = analyze(students, skills)
        create_charts(students, skills)
        recent = students[["roll_no","department","graduation_year","placement_status","company","role","package_lpa"]].head(100).fillna("").to_dict(orient="records")
        return render_template("detail.html", error=None, section_name=allowed_sections[section_name],
                               section_key=section_name, stats=stats, recent=recent,
                               departments=stats["department"], skills=stats["skills"])
    except Error as e:
        return render_template("detail.html", error="Database connection failed. Check .env settings and import schema.sql + seed.sql. Details: " + str(e),
                               section_name=allowed_sections[section_name], section_key=section_name,
                               stats=None, recent=[], departments=[], skills=[])
    except Exception as e:
        return render_template("detail.html", error="Could not load section: " + str(e),
                               section_name=allowed_sections[section_name], section_key=section_name,
                               stats=None, recent=[], departments=[], skills=[])

@app.route("/api/summary")
def api_summary():
    try:
        students, skills = fetch_data()
        return jsonify(analyze(students, skills))
    except Error as e:
        return jsonify({"error": "Database connection failed", "details": str(e)}), 500

@app.route("/api/students")
def api_students():
    department = request.args.get("department", "").strip()
    status = request.args.get("status", "").strip()
    year = request.args.get("year", "").strip()
    query = """
        SELECT s.student_id, s.roll_no, s.department, s.graduation_year,
               s.eligible, s.placement_status, p.company, p.role, p.package_lpa
        FROM students s LEFT JOIN placements p ON s.student_id = p.student_id
        WHERE 1=1
    """
    params = []
    if department:
        query += " AND s.department = %s"; params.append(department)
    if status:
        if status not in ["Placed", "Eligible - Not Placed", "Not Eligible"]:
            return jsonify({"error": "Invalid status filter"}), 400
        query += " AND s.placement_status = %s"; params.append(status)
    if year:
        try: year_value = int(year)
        except ValueError: return jsonify({"error": "Year must be an integer"}), 400
        if year_value < 2020 or year_value > 2040:
            return jsonify({"error": "Year must be between 2020 and 2040"}), 400
        query += " AND s.graduation_year = %s"; params.append(year_value)
    query += " ORDER BY s.student_id LIMIT 500"
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, tuple(params))
            return jsonify({"count_returned": cursor.rowcount, "limit": 500, "students": cursor.fetchall()})
        finally: conn.close()
    except Error as e:
        return jsonify({"error": "Database query failed", "details": str(e)}), 500

@app.route("/api/reports/<report_name>")
def report_image(report_name):
    allowed = {"department_placement_rate.png", "package_distribution.png", "top_skills.png"}
    if report_name not in allowed:
        return jsonify({"error": "Unknown report"}), 404
    path = os.path.join("reports", report_name)
    if not os.path.exists(path):
        try:
            students, skills = fetch_data(); create_charts(students, skills)
        except Exception as e:
            return jsonify({"error": "Could not generate report", "details": str(e)}), 500
    return send_file(path, mimetype="image/png")

@app.route("/api/export/department.csv")
def export_department():
    try:
        students, skills = fetch_data()
        stats = analyze(students, skills)
        output = StringIO()
        pd.DataFrame(stats["department"]).to_csv(output, index=False)
        output.seek(0)
        return send_file(BytesIO(output.getvalue().encode("utf-8")), mimetype="text/csv", as_attachment=True, download_name="department_placement_report.csv")
    except Exception as e:
        return jsonify({"error": "Could not export report", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
