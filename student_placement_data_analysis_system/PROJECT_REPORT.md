# Project Report: Student Placement Data Analysis System

## 1. Abstract
The Student Placement Data Analysis System is a small web application that summarizes placement outcomes using Python, Flask, MySQL, Pandas, NumPy and Matplotlib. It presents placement rate, department comparisons, package statistics and common student skills through a dashboard and REST APIs.

## 2. Problem statement
Placement data can be difficult to interpret when student, skill and offer information is stored in separate records. The system organizes these records relationally and produces consistent aggregate reports that help users understand placement outcomes.

## 3. Objectives
- Store student, skill and placement data in normalized relational tables.
- Maintain relationships through primary and foreign keys.
- Define a consistent placement-rate denominator.
- Analyze department outcomes, package distributions and listed skills.
- Provide a simple dashboard, API endpoints and chart exports.
- Use fictional data and avoid exposing personal student details.

## 4. Scope
The project uses synthetic data and supports aggregate placement analysis. It does not predict individual student outcomes, verify skill proficiency, or represent official university placement statistics.

## 5. Technology stack
- Python: application logic and validation
- Flask: web dashboard and REST endpoints
- MySQL: persistent relational storage
- Pandas: joins, cleaning, grouping and summaries
- NumPy: safe numerical calculations
- Matplotlib: charts served as PNG images
- HTML/CSS: responsive, minimal dashboard

## 6. Database design
- `students`: one row per fictional student; primary key `student_id`
- `skills`: unique skill dictionary; primary key `skill_id`
- `student_skills`: many-to-many mapping; composite primary key `(student_id, skill_id)`
- `placements`: one placement per student in this version; foreign key to `students` and unique `student_id`

## 7. Dataset
The included dataset contains 2,500 fictional student records, 9,919 student-skill links and 1,242 placement records. Departments, roles, companies, graduation years, skills and packages are generated for demonstration.

## 8. Analysis methodology
Placement rate = (number of unique eligible students with placement status `Placed` / total eligible students) × 100. Not-eligible students are excluded from the denominator. Packages are recorded in LPA. Mean, median and maximum package are calculated over placed students with valid package values. Skill counts use distinct student IDs to avoid double counting.

## 9. Visualizations
1. Placement rate by department: compares placement outcomes among eligible students.
2. Package distribution: histogram of package values for placed students, in LPA.
3. Top 10 listed skills: counts how many students list each skill.

Each chart includes a title, axis labels and units where applicable.

## 10. Testing
Test normal API calls, valid department/status/year filters, invalid status values, invalid years, database connection failures, unknown chart names and CSV export. Detailed test checklist is in `README.md`.

## 11. Security and data ethics
Credentials are stored in a local `.env` file excluded from version control. SQL filter values use parameterized queries. The data is synthetic. The dashboard shows only a small roll-number preview, and aggregate charts do not expose sensitive personal information.

## 12. Limitations and future improvements
The data is synthetic and cannot be used to make real-world placement claims. Future versions could add role-based authentication, pagination, multiple-offer tracking, date filters, CSV upload validation and a larger test suite.
