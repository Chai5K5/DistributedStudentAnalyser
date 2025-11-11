## Project Information

* Project Name: Distributed Student Analyzer
* Student Name: Chaitanya Sharma
* UID: 25MCD10056
* Course: MCA Data Science (DS)
* Department: UIC (University Institute of Computing)
* Subject: Python Programming (25CAH-606)
* Semester: 1st

## Project Overview

Distributed Student Analyser is a Python-based desktop app for managing and analyzing student records across branches.\ 
Built with CustomTkinter, SQLite, and Matplotlib, it supports quick CRUD operations, sorting, and searching through a\ 
modern interface.\
The dashboard also includes a Summary Statistics panel that visualizes branch-wise performance, marks trends, and\ 
attendance data—automatically highlighting students with attendance below 75%.

## 🚀 Features Implemented
- Add, update, delete, and view student records  
- Sort and search students using merge sort and binary search  
- Summary Statistics window with branch-wise analysis  
- Line and scatter plots for marks and attendance trends  
- Automatic highlighting of debarred students (attendance < 75%)  
- Clean, centered dialogs and progress feedback 
    
## Tech Stack

* Frontend/UI: CustomTkinter (modern Tkinter interface)
* Backend: SQLite (local database for student records)
* Visualization: Matplotlib, NumPy
* Language: Python

## 🖥️ How to Run
1. **Clone the repository**
   
       git clone https://github.com/Chai5K5/DistributedStudentAnalyser.git
       cd DistributedStudentAnalyser

2. Before running the project, it’s recommended to use a virtual environment to keep dependencies isolated.
    #### **For Windows**
        python -m venv venv
        venv\Scripts\activate
    #### **For Mac**
        python3 -m venv venv
        source venv/bin/activate
3. Install libraries
   
       pip install customtkinter matplotlib numpy pandas
4. Run the following command
   
       python ui/dashboard.py

## ⚙️ Database Setup (MySQL Distributed Backend)

This project uses **MySQL stored procedures** to manage distributed student records across multiple databases (horizontal fragmentation).

### 🧩 Step 1: Create Databases
Run the SQL script `database/initial_setup.sql` in MySQL Workbench to create the distributed databases:
- `db_cse`
- `db_aiml`
- `db_ds`
- `db_cc`

### 🧱 Step 2: Create Stored Procedures
Execute `database/distributed_backend.sql` in MySQL Workbench.
It defines the following backend procedures:
- `add_student`
- `update_student`
- `delete_student`
- `fetch_all_students`
- `filter_students`

### ⚡ Step 3: Run the Application
Activate your Python environment and run:

```bash
python ui/dashboard.py

