import time
import sys, os
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_handler import (
    fetch_all_students,
    add_student,
    update_student,
    delete_student,
    search_students
)
from backend.algorithm_utils import merge_sort, binary_search


# ------------------ Helpers ------------------

def center_window(win, parent, width, height):
    parent.update_idletasks()
    try:
        parent_w, parent_h, parent_x, parent_y = (
            int(v) for v in parent.winfo_geometry().replace('x', '+').split('+')
        )
        x = parent_x + (parent_w - width) // 2
        y = parent_y + (parent_h - height) // 2
    except Exception:
        s_w, s_h = parent.winfo_screenwidth(), parent.winfo_screenheight()
        x, y = (s_w - width) // 2, (s_h - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")
    win.update_idletasks()


# ------------------ Dialogs ------------------

class ModernDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, type="info"):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#1E1E1E")

        color_map = {
            "info": "#0D6EFD",
            "success": "#198754",
            "warning": "#FFC107",
            "error": "#DC3545"
        }

        ctk.CTkLabel(
            self, text=title, font=("Helvetica", 18, "bold"),
            text_color=color_map.get(type, "#0D6EFD")
        ).pack(pady=(20, 8))
        ctk.CTkLabel(
            self, text=message, font=("Helvetica", 14),
            text_color="#F8F9FA", wraplength=360, justify="center"
        ).pack(pady=(4, 12))
        ctk.CTkButton(
            self, text="OK", width=100,
            fg_color=color_map.get(type, "#0D6EFD"),
            command=self.destroy
        ).pack(pady=(4, 16))
        center_window(self, parent, 420, 200)


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.transient(parent)
        self.result = None
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#1E1E1E")

        ctk.CTkLabel(self, text=title, font=("Helvetica", 18, "bold"), text_color="#FFC107").pack(pady=(18, 10))
        ctk.CTkLabel(self, text=message, font=("Helvetica", 14), text_color="#E9ECEF",
                     wraplength=360, justify="center").pack(pady=8)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=12)
        ctk.CTkButton(btn_frame, text="Yes", width=90, fg_color="#198754", command=self.on_yes).pack(side="left", padx=12)
        ctk.CTkButton(btn_frame, text="No", width=90, fg_color="#DC3545", command=self.on_no).pack(side="right", padx=12)
        center_window(self, parent, 420, 200)
        self.wait_window()

    def on_yes(self): self.result, _ = True, self.destroy()
    def on_no(self): self.result, _ = False, self.destroy()


class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, prompt, input_type="text"):
        super().__init__(parent)
        self.transient(parent)
        self.value = None
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#1E1E1E")

        ctk.CTkLabel(self, text=prompt, font=("Helvetica", 15, "bold"),
                     text_color="#E9ECEF", wraplength=360, justify="center").pack(pady=(22, 8))

        if input_type == "int":
            validate = (self.register(lambda v: v.isdigit() or v == ""), "%P")
            self.entry = ctk.CTkEntry(self, validate="key", validatecommand=validate)
        elif input_type == "float":
            validate = (self.register(lambda v: v.replace(".", "", 1).isdigit() or v == ""), "%P")
            self.entry = ctk.CTkEntry(self, validate="key", validatecommand=validate)
        else:
            self.entry = ctk.CTkEntry(self)

        self.entry.pack(pady=6, padx=30, fill="x")
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=12)
        ctk.CTkButton(btn_frame, text="OK", width=90, fg_color="#0D6EFD", command=self.submit).pack(side="left", padx=12)
        ctk.CTkButton(btn_frame, text="Cancel", width=90, fg_color="#DC3545", command=self.cancel).pack(side="right", padx=12)
        center_window(self, parent, 420, 180)
        self.wait_window()

    def submit(self):
        val = self.entry.get().strip()
        if val != "":
            self.value = val
        self.destroy()

    def cancel(self): self.destroy()


# ------------------ Main Dashboard ------------------

class StudentDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Distributed Student Record Dashboard")
        self.root.geometry("950x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.setup_ui()
        self.load_data()

    # ------------------ UI Setup ------------------

    def setup_ui(self):
        title = ctk.CTkLabel(self.root, text="📊 Distributed Student Record Analyzer",
                             font=("Helvetica", 20, "bold"), text_color="#E9ECEF")
        title.pack(pady=12)

        btn_outer = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_outer.pack(pady=10, fill="x")
        btn_inner = ctk.CTkFrame(btn_outer, fg_color="#212529", corner_radius=12)
        btn_inner.place(relx=0.5, rely=0.5, anchor="n")
        button_cfg = {"width": 110, "height": 34, "corner_radius": 8, "font": ("Helvetica", 13, "bold")}

        ctk.CTkButton(btn_inner, text="⟳", width=40, height=26, fg_color="#0D6EFD",
                      font=("Helvetica", 18, "bold"), command=self.load_data).grid(row=0, column=0, padx=12, pady=12)

        crud_frame = ctk.CTkFrame(btn_inner, fg_color="transparent")
        crud_frame.grid(row=0, column=1, padx=12)
        ctk.CTkButton(crud_frame, text="➕ Add", fg_color="#198754", command=self.add_student_ui, **button_cfg).pack(side="left", padx=6)
        ctk.CTkButton(crud_frame, text="✏ Update", fg_color="#FFC107", text_color="black",
                      command=self.update_student_ui, **button_cfg).pack(side="left", padx=6)
        ctk.CTkButton(crud_frame, text="🗑 Delete", fg_color="#DC3545", command=self.delete_student_ui, **button_cfg).pack(side="left", padx=6)

        sort_frame = ctk.CTkFrame(btn_inner, fg_color="transparent")
        sort_frame.grid(row=0, column=2, padx=20)
        ctk.CTkButton(sort_frame, text="⬆ Sort", fg_color="#6610F2", command=self.sort_data, **button_cfg).pack(side="left", padx=6)
        ctk.CTkButton(sort_frame, text="🔍 Search", fg_color="#20C997", command=self.search_data, **button_cfg).pack(side="left", padx=6)
        ctk.CTkButton(btn_inner, text="📈 Summary Stats", fg_color="#6F42C1",
                      command=self.show_summary, **button_cfg).grid(row=0, column=3, padx=16)

        # Table
        table_frame = ctk.CTkFrame(self.root, fg_color="#343A40", corner_radius=12)
        table_frame.pack(pady=12, padx=25, fill="both", expand=True)
        columns = ("Roll No", "Name", "Branch", "Marks", "Attendance")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#212529", foreground="white", rowheight=28, fieldbackground="#212529", font=("Helvetica", 12))
        style.configure("Treeview.Heading", background="#495057", foreground="white", font=("Helvetica", 13, "bold"))
        style.map("Treeview", background=[("selected", "#0D6EFD")])
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=160)
        self.tree.pack(pady=10, fill="both", expand=True)
        self.progress_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.progress_container.pack(side="bottom", pady=12)

    # ------------------ Data Load ------------------

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for c in self.progress_container.winfo_children():
            c.destroy()
        progress = ctk.CTkProgressBar(self.progress_container, width=480, height=18)
        progress.pack()
        progress.set(0)
        self.root.update_idletasks()

        students = fetch_all_students()
        total = len(students) if students else 1
        for i, s in enumerate(students):
            time.sleep(0.02)
            tag = "debarred" if s[4] < 75 else ""
            self.tree.insert("", "end", values=s, tags=(tag,))
            progress.set((i + 1) / total)
            self.root.update_idletasks()
        self.tree.tag_configure("debarred", foreground="#FF4D4D", background="#3B0000")
        progress.destroy()
        self.root.after(200, lambda: ModernDialog(self.root, "Data Loaded", f"✅ Loaded {len(students)} student records!", "success"))

    # ------------------ CRUD ------------------

    def ask_sequence_inputs(self, inputs):
        results = []
        for title, prompt, typ in inputs:
            dlg = CustomInputDialog(self.root, title, prompt, typ)
            if dlg.value is None:
                ModernDialog(self.root, "Cancelled", "Operation cancelled.", "info")
                return None
            results.append(dlg.value)
        return results

    def add_student_ui(self):
        try:
            prompts = [
                ("Add Student", "Enter Roll No:", "int"),
                ("Add Student", "Enter Name:", "text"),
                ("Add Student", "Enter Branch (CSE/AIML/DS/CC):", "text"),
                ("Add Student", "Enter Marks:", "float"),
                ("Add Student", "Enter Attendance:", "float"),
            ]
            vals = self.ask_sequence_inputs(prompts)
            if not vals:
                return
            roll_no, name, branch, marks, attendance = vals
            success = add_student(int(roll_no), name, branch, float(marks), float(attendance))
            ModernDialog(self.root, "Result",
                         "✅ Student added successfully!" if success else "❌ Failed to add student.",
                         "success" if success else "error")
            self.load_data()
        except Exception as e:
            ModernDialog(self.root, "Error", f"⚠ {str(e)}", "error")

    def update_student_ui(self):
        prompts = [
            ("Update Student", "Enter Roll No to update:", "int"),
            ("Update Student", "Enter Branch (CSE/AIML/DS/CC):", "text"),
            ("Update Student", "Enter new Marks:", "float"),
            ("Update Student", "Enter new Attendance:", "float"),
        ]
        vals = self.ask_sequence_inputs(prompts)
        if not vals:
            return
        roll_no, branch, marks, attendance = vals
        success = update_student(int(roll_no), branch, float(marks), float(attendance))
        ModernDialog(self.root, "Update", "✅ Record updated." if success else "❌ Update failed.",
                     "success" if success else "error")
        self.load_data()

    def delete_student_ui(self):
        prompts = [
            ("Delete Student", "Enter Roll No:", "int"),
            ("Delete Student", "Enter Branch (CSE/AIML/DS/CC):", "text"),
        ]
        vals = self.ask_sequence_inputs(prompts)
        if not vals:
            return
        roll_no, branch = vals
        confirm = ConfirmDialog(self.root, "Confirm Delete", f"Delete student {roll_no} from {branch}?")
        if confirm.result:
            success = delete_student(int(roll_no), branch)
            ModernDialog(self.root, "Delete", "🗑 Record deleted." if success else "❌ Delete failed.",
                         "success" if success else "error")
            self.load_data()

    # ------------------ Algorithms ------------------

    def sort_data(self):
        students = fetch_all_students()
        sorted_students = merge_sort(students, key_index=3)
        self.tree.delete(*self.tree.get_children())
        for s in sorted_students:
            tag = "debarred" if s[4] < 75 else ""
            self.tree.insert("", "end", values=s, tags=(tag,))
        self.tree.tag_configure("debarred", foreground="#FF4D4D", background="#3B0000")
        ModernDialog(self.root, "Merge Sort", "✅ Sorted by marks.", "info")

    def search_data(self):
        prompts = [
            ("Distributed Search", "Enter keyword (name, leave blank for all):", "text"),
            ("Distributed Search", "Min Marks (blank for none):", "float"),
            ("Distributed Search", "Max Marks (blank for none):", "float"),
            ("Distributed Search", "Branch (CSE/AIML/DS/CC or blank):", "text"),
        ]
        vals = self.ask_sequence_inputs(prompts)
        if not vals:
            return
        keyword, min_m, max_m, branch = vals
        min_m = float(min_m) if min_m else None
        max_m = float(max_m) if max_m else None
        branch = branch.upper() if branch else None
        results = search_students(keyword or None, min_m, max_m, branch)
        self.tree.delete(*self.tree.get_children())
        for s in results:
            tag = "debarred" if s[4] < 75 else ""
            self.tree.insert("", "end", values=s, tags=(tag,))
        self.tree.tag_configure("debarred", foreground="#FF4D4D", background="#3B0000")
        ModernDialog(self.root, "Search", f"🔍 Found {len(results)} record(s).", "info")

    # ------------------ Summary ------------------

    def show_summary(self):
        students = fetch_all_students()
        if not students:
            ModernDialog(self.root, "No Data", "No records found.", "warning")
            return
        branches, debarred = {}, 0
        for s in students:
            b = s[2].upper()
            branches.setdefault(b, {"marks": [], "attendance": []})
            branches[b]["marks"].append(s[3])
            branches[b]["attendance"].append(s[4])
            if s[4] < 75:
                debarred += 1

        win = ctk.CTkToplevel(self.root)
        win.title("Summary")
        win.configure(fg_color="#1E1E1E")
        center_window(win, self.root, 820, 520)
        win.transient(self.root)
        win.grab_set()

        ctk.CTkLabel(win, text="📈 Branch Summary Statistics",
                     font=("Helvetica", 20, "bold"), text_color="#F8F9FA").pack(pady=(20, 10))
        scroll = ctk.CTkScrollableFrame(win, width=780, height=400, fg_color="#2B2B2B")
        scroll.pack(pady=5, padx=10, fill="both", expand=True)
        text = ""
        for b, vals in branches.items():
            m, a = np.array(vals["marks"]), np.array(vals["attendance"])
            text += f"─── {b} BRANCH ───\n"
            text += f"Avg Marks: {m.mean():.2f}\nMax Marks: {m.max():.2f}\nMin Marks: {m.min():.2f}\n"
            text += f"Avg Attendance: {a.mean():.2f}%\n\n"
        text += f"🚫 Total Debarred: {debarred}\n"
        box = ctk.CTkTextbox(scroll, width=440, height=220)
        box.pack(pady=10)
        box.insert("1.0", text)
        box.configure(state="disabled")

        fig, axs = plt.subplots(2, 1, figsize=(8, 8), facecolor="#1E1E1E")
        fig.subplots_adjust(hspace=0.45)
        ax1, ax2 = axs
        ax1.set_facecolor("#2B2B2B")
        ax2.set_facecolor("#2B2B2B")

        branches_list = list(branches.keys())
        avg_marks = [np.mean(branches[b]["marks"]) for b in branches_list]
        avg_att = [np.mean(branches[b]["attendance"]) for b in branches_list]

        ax1.bar(branches_list, avg_marks)
        ax1.set_title("Average Marks by Branch", color="white")
        ax1.set_ylabel("Marks")
        ax1.tick_params(colors="white")
        ax2.bar(branches_list, avg_att)
        ax2.set_title("Average Attendance by Branch", color="white")
        ax2.set_ylabel("%")
        ax2.tick_params(colors="white")
        ax2.yaxis.set_major_formatter(mticker.PercentFormatter())

        canvas = FigureCanvasTkAgg(fig, master=scroll)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)


if __name__ == "__main__":
    root = ctk.CTk()
    StudentDashboard(root)
    root.mainloop()
