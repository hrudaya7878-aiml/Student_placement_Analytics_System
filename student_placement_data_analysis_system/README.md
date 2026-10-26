# Student Placement Data Analysis System

A clean Flask + MySQL + Pandas + NumPy + Matplotlib project for a Python class submission. All included student data is **synthetic and fictional**.

## Included data
- **2,500 student records** in `data/students.csv`
- **9,919 student-skill links** in `data/student_skills.csv`
- **1,242 placement records** in `data/placements.csv`
- `seed.sql` loads the sample records into MySQL.
- `schema.sql` defines tables, primary/foreign keys, constraints and a unique placement-per-student rule.

Packages are in **LPA (lakhs per annum)**. Placement rate = unique students with status `Placed` ÷ eligible students × 100. Students marked not eligible are excluded from the denominator. A placed student has one placement row; the database prevents duplicate placement rows for the same student.

## Requirements
- Python 3.10+
- MySQL 8+
- A terminal / command prompt

## Setup (Windows)
1. Extract the ZIP and open the project folder in VS Code.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
4. In MySQL Workbench, open and run `schema.sql`, then run `seed.sql`. `seed.sql` starts by clearing existing rows from these project tables, so use it only for this sample project database.
5. Copy `.env.example` to `.env` and fill in your MySQL password:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_actual_password
   DB_NAME=student_placement_db
   FLASK_DEBUG=false
   ```
   Keep `.env` private and do not upload it to GitHub.
6. Start the website:
   ```bash
   python app.py
   ```
7. Open `http://127.0.0.1:5000` in your browser.

## Main routes / APIs
| Route | Purpose |
|---|---|
| `/` | Dashboard with summary cards and three charts |
| `/api/summary` | Aggregate placement, department, package and skill summary as JSON |
| `/api/students` | Student data, with optional filters and a 500-row response cap |
| `/api/students?department=CSE-AIML` | Filter by department |
| `/api/students?status=Placed` | Filter by placement status |
| `/api/students?year=2027` | Filter by graduation year |
| `/api/reports/department_placement_rate.png` | Department placement-rate chart |
| `/api/reports/package_distribution.png` | Package distribution chart |
| `/api/reports/top_skills.png` | Top skills chart |
| `/api/export/department.csv` | Download department summary as CSV |

## Data analysis methodology
- **Pandas:** joins students to placements, groups by department and skill, counts unique students per skill and prepares summary reports.
- **NumPy:** calculates department placement rates safely when the denominator is zero.
- **NumPy/Pandas statistics:** mean, median and maximum package for placed students.
- **Matplotlib:** generates charts with titles, axes, units and gridlines.
- **SQL safety:** parameterized values are used in the student filter endpoint. Database credentials are read from environment variables.
- **Privacy:** only fictional sample data is included. Aggregate reports do not show names, phone numbers or personal medical/banking data.

## Suggested testing checklist
- [ ] Dashboard opens with the database running.
- [ ] `/api/summary` returns JSON.
- [ ] `/api/students?department=CSE-AIML` filters the result.
- [ ] `/api/students?status=Invalid` returns HTTP 400.
- [ ] `/api/students?year=abc` returns HTTP 400.
- [ ] Unknown report image returns HTTP 404.
- [ ] Wrong database password displays a useful setup error.
- [ ] Department CSV export downloads successfully.

## Limitations
- Data is generated for demonstration and is not a real placement prediction or official university report.
- The dataset contains one placement per student. Multiple-offer comparison is outside the current scope.
- Skill counts measure students who list a skill, not verified proficiency or employer demand.
- Package values are illustrative, not salary promises or market benchmarks.


## Dashboard navigation update
The home page now shows section headings/cards only. Click a card to open the detailed view for Placement Overview, Department Analysis, Package Analysis, Skill Demand, Student Records, or Charts & Reports. Each detail page includes a link back to the home page.
