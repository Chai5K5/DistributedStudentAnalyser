CREATE DATABASE db_cse;
CREATE DATABASE db_ds;
CREATE DATABASE db_cc;
CREATE DATABASE db_aiml;
USE db_cse;
USE db_aiml;
USE db_ds;
USE db_cc;

select * from students;
select * from departments;
select * from courses;

CREATE TABLE students (
    roll_no INT PRIMARY KEY,
    name VARCHAR(100),
    branch VARCHAR(20),
    marks FLOAT,
    attendance FLOAT
);
CREATE TABLE courses (
    course_id   INT PRIMARY KEY,
    course_name VARCHAR(100),
    credits     INT
);
CREATE TABLE departments (
    dept_id     INT PRIMARY KEY,
    dept_name   VARCHAR(50)
);
USE db_cse;
INSERT INTO students VALUES
(101, 'Aman Sharma', 'CSE', 86.5, 92),
(102, 'Riya Gupta', 'CSE', 73.4, 88),
(103, 'Karan Patel', 'CSE', 91.0, 95);

USE db_aiml;
INSERT INTO students VALUES
(201, 'Ananya Verma', 'AIML', 89.2, 90),
(202, 'Harsh Mehta', 'AIML', 67.8, 82),
(203, 'Sanya Iyer', 'AIML', 94.6, 97);

USE db_ds;
INSERT INTO students (roll_no, name, branch, marks, attendance) VALUES
(301, 'Ananya Goyal', 'DS', 89, 93),
(302, 'Karan Bansal', 'DS', 76, 88),
(303, 'Tanya Oberoi', 'DS', 94, 97),
(304, 'Rohit Sharma', 'DS', 82, 91),
(305, 'Ishita Suri', 'DS', 68, 85),
(306, 'Arjun Kapoor', 'DS', 73, 92),
(307, 'Simran Khanna', 'DS', 90, 95),
(308, 'Harshdeep Gill', 'DS', 81, 89),
(309, 'Priya Nanda', 'DS', 78, 87),
(310, 'Vikas Bhardwaj', 'DS', 85, 90);

USE db_cc;
INSERT INTO students (roll_no, name, branch, marks, attendance) VALUES
(401, 'Neha Talwar', 'CC', 84, 92),
(402, 'Raman Joshi', 'CC', 79, 87),
(403, 'Sanya Malhotra', 'CC', 88, 93),
(404, 'Aayush Rana', 'CC', 91, 96),
(405, 'Divya Kapoor', 'CC', 72, 84),
(406, 'Manish Gupta', 'CC', 65, 78),
(407, 'Ritika Sehgal', 'CC', 90, 97),
(408, 'Arnav Bedi', 'CC', 77, 89),
(409, 'Aditi Chopra', 'CC', 85, 91),
(410, 'Sarthak Mehta', 'CC', 93, 94);

-- Replicated
INSERT INTO departments VALUES
(1, 'Computer Science'), (2, 'Artificial Intelligence'),
(3, 'Data Science'), (4, 'Cloud Computing');
INSERT INTO courses VALUES
(101, 'DBMS', 4),
(102, 'Distributed Systems', 4),
(103, 'Data Mining', 3),
(104, 'Cloud Security', 3);



