import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# add backend to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_handler import fetch_all_students
from backend.algorithm_utils import merge_sort, binary_search

class StudentAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Distributed Student Record Analyzer")
        self.root.geometry("800x500")
        self.root.configure(bg="#F8F9FA")

        self.setup_ui()

    def setup_ui(self):
        # Title Label
        title = tk.Label(
            self.root, text="Distributed Student Record Analyzer",
            font=("Helvetica", 18, "bold"), bg="#F8F9FA", fg="#212529"
        )
        title.pack(pady=15)

        # Buttons frame
        btn_frame = tk.Frame(self.root, bg="#F8F9FA")
        btn_frame.pack(pady=10)

        refresh_btn = tk.Button(
            btn_frame, text="🔄 Refresh Data", bg="#0D6EFD", fg="white",
            font=("Arial", 11, "bold"), relief="ridge", command=self.load_data
        )
        refresh_btn.grid(row=0, column=0, padx=10)

        sort_btn = tk.Button(
            btn_frame, text="⬆ Sort by Marks (Merge Sort)", bg="#198754", fg="white",
            font=("Arial", 11, "bold"), relief="ridge", command=self.sort_data
        )
        sort_btn.grid(row=0, column=1, padx=10)

        search_btn = tk.Button(
            btn_frame, text="🔍 Search by Roll No (Binary Search)", bg="#FFC107", fg="black",
            font=("Arial", 11, "bold"), relief="ridge", command=self.search_data
        )
        search_btn.grid(row=0, column=2, padx=10)

        # Table
        columns = ("Roll No", "Name", "Branch", "Marks", "Attendance")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.CENTER)

        self.tree.pack(pady=10)
        self.load_data()

    def load_data(self):
        """Fetch and display all students."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        students = fetch_all_students()
        for s in students:
            self.tree.insert("", tk.END, values=s)

    def sort_data(self):
        """Use Merge Sort to sort students by marks."""
        students = fetch_all_students()
        sorted_students = merge_sort(students, key_index=3)  # sort by marks (index 3)

        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in sorted_students:
            self.tree.insert("", tk.END, values=s)

        messagebox.showinfo("Merge Sort", "Students sorted by marks successfully!")

    def search_data(self):
        """Use Binary Search to find a student by roll number."""
        students = fetch_all_students()
        # Make sure it's sorted by roll number (index 0)
        students.sort(key=lambda x: x[0])

        roll_no = simpledialog.askinteger("Binary Search", "Enter Roll No to search:")
        if roll_no is None:
            return

        result = binary_search(students, roll_no)
        if result:
            messagebox.showinfo("Result", f"✅ Found: {result[1]} ({result[2]})\nMarks: {result[3]}, Attendance: {result[4]}")
        else:
            messagebox.showwarning("Not Found", "No student with that roll number.")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentAnalyzerApp(root)
    root.mainloop()
