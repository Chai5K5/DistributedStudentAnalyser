# dashboard.py
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys, os

# add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_handler import (
    fetch_all_students,
    add_student,
    update_student,
    delete_student
)
from backend.algorithm_utils import merge_sort, binary_search


class StudentDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Distributed Student Record Dashboard")
        self.root.geometry("850x550")
        self.root.configure(bg="#F8F9FA")

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        title = tk.Label(
            self.root,
            text="📊 Distributed Student Record Analyzer",
            font=("Helvetica", 17, "bold"),
            bg="#F8F9FA",
            fg="#212529",
        )
        title.pack(pady=15)

        btn_frame = tk.Frame(self.root, bg="#F8F9FA")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="🔄 Refresh", bg="#0D6EFD", fg="white", command=self.load_data).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="➕ Add", bg="#198754", fg="white", command=self.add_student_ui).grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="✏ Update", bg="#FFC107", fg="black", command=self.update_student_ui).grid(row=0, column=2, padx=8)
        tk.Button(btn_frame, text="🗑 Delete", bg="#DC3545", fg="white", command=self.delete_student_ui).grid(row=0, column=3, padx=8)
        tk.Button(btn_frame, text="⬆ Sort (Merge Sort)", bg="#6610F2", fg="white", command=self.sort_data).grid(row=0, column=4, padx=8)
        tk.Button(btn_frame, text="🔍 Search (Binary Search)", bg="#20C997", fg="white", command=self.search_data).grid(row=0, column=5, padx=8)

        columns = ("Roll No", "Name", "Branch", "Marks", "Attendance")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.CENTER)
        self.tree.pack(pady=15)

    # ------------------ Data Load ------------------

    def load_data(self):
        """Fetch and display all students."""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Create a progress bar
        progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        progress.pack(pady=10)
        progress["maximum"] = 100
        progress["value"] = 0
        self.root.update_idletasks()

        students = fetch_all_students()
    
    # Simulate progress while loading
        for i, s in enumerate(students):
            time.sleep(0.2)  # simulate load
            self.tree.insert("", tk.END, values=s)
            progress["value"] = ((i + 1) / len(students)) * 100
            self.root.update_idletasks()

        progress.destroy()
        messagebox.showinfo("Data Loaded", f"Loaded {len(students)} student records!")

    # ------------------ CRUD Operations ------------------

    def add_student_ui(self):
        try:
            roll_no = simpledialog.askinteger("Add Student", "Enter Roll No:")
            if roll_no is None:
                return
            name = simpledialog.askstring("Add Student", "Enter Name:")
            branch = simpledialog.askstring("Add Student", "Enter Branch (CSE/AIML):")
            marks = simpledialog.askfloat("Add Student", "Enter Marks:")
            attendance = simpledialog.askfloat("Add Student", "Enter Attendance:")

            success = add_student(roll_no, name, branch, marks, attendance)
            if success:
                messagebox.showinfo("Success", "✅ Student added successfully!")
                self.load_data()
            else:
                messagebox.showerror("Error", "❌ Failed to add student.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_student_ui(self):
        roll_no = simpledialog.askinteger("Update Student", "Enter Roll No to update:")
        if roll_no is None:
            return
        branch = simpledialog.askstring("Update Student", "Enter Branch (CSE/AIML):")
        new_marks = simpledialog.askfloat("Update Student", "Enter new Marks:")
        new_attendance = simpledialog.askfloat("Update Student", "Enter new Attendance:")

        success = update_student(roll_no, branch, new_marks, new_attendance)
        if success:
            messagebox.showinfo("Updated", "✅ Student record updated.")
            self.load_data()
        else:
            messagebox.showwarning("Not Found", "❌ Student not found or update failed.")

    def delete_student_ui(self):
        roll_no = simpledialog.askinteger("Delete Student", "Enter Roll No to delete:")
        if roll_no is None:
            return
        branch = simpledialog.askstring("Delete Student", "Enter Branch (CSE/AIML):")

        confirm = messagebox.askyesno("Confirm Delete", f"Delete student {roll_no} from {branch}?")
        if not confirm:
            return

        success = delete_student(roll_no, branch)
        if success:
            messagebox.showinfo("Deleted", "🗑 Student record deleted.")
            self.load_data()
        else:
            messagebox.showwarning("Error", "❌ Could not delete student.")

    # ------------------ Algorithm Features ------------------

    def sort_data(self):
        students = fetch_all_students()
        sorted_students = merge_sort(students, key_index=3)  # sort by marks
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in sorted_students:
            self.tree.insert("", tk.END, values=s)
        messagebox.showinfo("Merge Sort", "✅ Students sorted by marks.")

    def search_data(self):
        students = fetch_all_students()
        students.sort(key=lambda x: x[0])  # sort by roll no
        roll_no = simpledialog.askinteger("Binary Search", "Enter Roll No to search:")
        if roll_no is None:
            return
        result = binary_search(students, roll_no)
        if result:
            messagebox.showinfo("Found", f"🎯 {result[1]} ({result[2]})\nMarks: {result[3]}, Attendance: {result[4]}")
        else:
            messagebox.showwarning("Not Found", "No student with that roll number found.")


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentDashboard(root)
    root.mainloop()
