CREATE DATABASE IF NOT EXISTS student_placement_db;
USE student_placement_db;

CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    department VARCHAR(40) NOT NULL,
    graduation_year SMALLINT NOT NULL,
    eligible BOOLEAN NOT NULL DEFAULT TRUE,
    placement_status ENUM('Placed','Eligible - Not Placed','Not Eligible') NOT NULL,
    CHECK (graduation_year BETWEEN 2020 AND 2040)
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS student_skills (
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (student_id, skill_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS placements (
    placement_id INT PRIMARY KEY,
    student_id INT NOT NULL,
    company VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    package_lpa DECIMAL(8,2) NOT NULL,
    placement_date DATE NOT NULL,
    status ENUM('Selected','Offer Accepted','Joined') NOT NULL DEFAULT 'Selected',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    CHECK (package_lpa > 0),
    UNIQUE KEY unique_student_placement (student_id)
);
