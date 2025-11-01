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
   
       pip install numpy pandas matplotlib seaborn streamlit
4. Run the following command
   
       python ui/dashboard.py
