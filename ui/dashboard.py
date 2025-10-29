# ui/dashboard.py
import time
import sys, os
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker
import numpy as np

# add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_handler import (
    fetch_all_students,
    add_student,
    update_student,
    delete_student
)
from backend.algorithm_utils import merge_sort, binary_search


# ------------------ Helpers ------------------

def center_window(win, parent, width, height):
    parent.update_idletasks()
    parent_geo = parent.winfo_geometry()
    try:
        parent_w, parent_h, parent_x, parent_y = (
            int(v) for v in parent_geo.replace('x', '+').split('+')
        )
    except Exception:
        s_w = parent.winfo_screenwidth()
        s_h = parent.winfo_screenheight()
        x = (s_w - width) // 2
        y = (s_h - height) // 2
    else:
        x = parent_x + (parent_w - width) // 2
        y = parent_y + (parent_h - height) // 2

    win.geometry(f"{width}x{height}+{x}+{y}")
    win.update_idletasks()


# ------------------ Modern Dialogs ------------------

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
        ).pack(pady=(20, 8), padx=12)

        ctk.CTkLabel(
            self, text=message, font=("Helvetica", 14),
            text_color="#F8F9FA", wraplength=360, justify="center"
        ).pack(pady=(4, 12), padx=12)

        ctk.CTkButton(
            self, text="OK", width=100,
            fg_color=color_map.get(type, "#0D6EFD"),
            command=self._on_ok
        ).pack(pady=(4, 16))

        center_window(self, parent, 420, 200)

    def _on_ok(self):
        self.destroy()


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.transient(parent)
        self.result = None
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#1E1E1E")

        ctk.CTkLabel(
            self, text=title, font=("Helvetica", 18, "bold"),
            text_color="#FFC107"
        ).pack(pady=(18, 10), padx=10)

        ctk.CTkLabel(
            self, text=message, font=("Helvetica", 14),
            text_color="#E9ECEF", wraplength=360, justify="center"
        ).pack(pady=8, padx=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=12)

        ctk.CTkButton(
            btn_frame, text="Yes", width=90,
            fg_color="#198754", command=self.on_yes
        ).pack(side="left", padx=12)

        ctk.CTkButton(
            btn_frame, text="No", width=90,
            fg_color="#DC3545", command=self.on_no
        ).pack(side="right", padx=12)

        center_window(self, parent, 420, 200)
        self.wait_window()

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()


class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, prompt, input_type="text"):
        super().__init__(parent)
        self.transient(parent)
        self.value = None
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#1E1E1E")

        ctk.CTkLabel(
            self, text=prompt, font=("Helvetica", 15, "bold"),
            text_color="#E9ECEF", wraplength=360, justify="center"
        ).pack(pady=(22, 8), padx=10)

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

    def cancel(self):
        self.value = None
        self.destroy()


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

    def setup_ui(self):
        title = ctk.CTkLabel(
            self.root,
            text="📊 Distributed Student Record Analyzer",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color="#E9ECEF"
        )
        title.pack(pady=12)

        btn_outer = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_outer.pack(pady=10, fill="x")

        btn_inner = ctk.CTkFrame(btn_outer, fg_color="#212529", corner_radius=10)
        btn_inner.place(relx=0.5, rely=0.5, anchor="n")

        button_config = {"width": 120, "height": 34, "corner_radius": 8, "font": ("Helvetica", 13, "bold")}

        ctk.CTkButton(btn_inner, text="🔄 Refresh", fg_color="#0D6EFD", command=self.load_data, **button_config).grid(row=0, column=0, padx=8, pady=10)
        ctk.CTkButton(btn_inner, text="➕ Add", fg_color="#198754", command=self.add_student_ui, **button_config).grid(row=0, column=1, padx=8, pady=10)
        ctk.CTkButton(btn_inner, text="✏ Update", fg_color="#FFC107", text_color="black", command=self.update_student_ui, **button_config).grid(row=0, column=2, padx=8, pady=10)
        ctk.CTkButton(btn_inner, text="🗑 Delete", fg_color="#DC3545", command=self.delete_student_ui, **button_config).grid(row=0, column=3, padx=8, pady=10)
        ctk.CTkButton(btn_inner, text="⬆ Sort", fg_color="#6610F2", command=self.sort_data, **button_config).grid(row=0, column=4, padx=8, pady=10)
        ctk.CTkButton(btn_inner, text="🔍 Search", fg_color="#20C997", command=self.search_data, **button_config).grid(row=0, column=5, padx=8, pady=10)
        ctk.CTkButton(btn_inner, text="📈 Summary Stats", fg_color="#6F42C1", command=self.show_summary, **button_config).grid(row=0, column=6, padx=8, pady=10)

        table_frame = ctk.CTkFrame(self.root, fg_color="#343A40", corner_radius=12)
        table_frame.pack(pady=12, padx=25, fill="both", expand=True)

        columns = ("Roll No", "Name", "Branch", "Marks", "Attendance")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#212529", foreground="white",
                        rowheight=28, fieldbackground="#212529", font=("Helvetica", 12))
        style.configure("Treeview.Heading", background="#495057", foreground="white", font=("Helvetica", 13, "bold"))
        style.map('Treeview', background=[('selected', '#0D6EFD')])

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=160)
        self.tree.pack(pady=10, fill="both", expand=True)

        self.progress_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.progress_container.pack(side="bottom", pady=12)

    def ask_sequence_inputs(self, inputs):
        results = []
        for title, prompt, typ in inputs:
            dlg = CustomInputDialog(self.root, title, prompt, typ)
            val = dlg.value
            if val is None:
                ModernDialog(self.root, "Cancelled", "Operation cancelled by user.", "info")
                return None
            results.append(val)
        return results

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for child in self.progress_container.winfo_children():
            child.destroy()
        progress = ctk.CTkProgressBar(self.progress_container, width=480, height=18)
        progress.pack()
        progress.set(0)
        self.root.update_idletasks()

        students = fetch_all_students()
        total = len(students) if students else 1

        for i, s in enumerate(students):
            time.sleep(0.05)
            tag = "debarred" if s[4] < 75 else ""
            self.tree.insert("", "end", values=s, tags=(tag,))
            progress.set((i + 1) / total)
            self.root.update_idletasks()

        self.tree.tag_configure("debarred", foreground="#FF4D4D", background="#3B0000")

        progress.destroy()
        self.root.after(200, lambda: ModernDialog(self.root, "Data Loaded", f"✅ Loaded {len(students)} student records!", "success"))

    # ------------------ CRUD Operations ------------------

    def add_student_ui(self):
        try:
            prompts = [
                ("Add Student", "Enter Roll No:", "int"),
                ("Add Student", "Enter Name:", "text"),
                ("Add Student", "Enter Branch (CSE/AIML):", "text"),
                ("Add Student", "Enter Marks:", "float"),
                ("Add Student", "Enter Attendance:", "float"),
            ]
            vals = self.ask_sequence_inputs(prompts)
            if vals is None:
                return
            roll_no, name, branch, marks, attendance = vals
            success = add_student(int(roll_no), name, branch, float(marks), float(attendance))
            if success:
                ModernDialog(self.root, "Success", "✅ Student added successfully!", "success")
                self.load_data()
            else:
                ModernDialog(self.root, "Error", "❌ Failed to add student.", "error")
        except Exception as e:
            ModernDialog(self.root, "Error", f"⚠ {str(e)}", "error")

    def update_student_ui(self):
        prompts = [
            ("Update Student", "Enter Roll No to update:", "int"),
            ("Update Student", "Enter Branch (CSE/AIML):", "text"),
            ("Update Student", "Enter new Marks:", "float"),
            ("Update Student", "Enter new Attendance:", "float"),
        ]
        vals = self.ask_sequence_inputs(prompts)
        if vals is None:
            return
        roll_no, branch, new_marks, new_attendance = vals
        try:
            success = update_student(int(roll_no), branch, float(new_marks), float(new_attendance))
            if success:
                ModernDialog(self.root, "Updated", "✅ Student record updated.", "success")
                self.load_data()
            else:
                ModernDialog(self.root, "Not Found", "❌ Student not found or update failed.", "warning")
        except Exception as e:
            ModernDialog(self.root, "Error", f"⚠ {str(e)}", "error")

    def delete_student_ui(self):
        prompts = [
            ("Delete Student", "Enter Roll No to delete:", "int"),
            ("Delete Student", "Enter Branch (CSE/AIML):", "text"),
        ]
        vals = self.ask_sequence_inputs(prompts)
        if vals is None:
            return
        roll_no, branch = vals
        confirm = ConfirmDialog(self.root, "Confirm Delete", f"Delete student {roll_no} from {branch}?")
        if not confirm.result:
            ModernDialog(self.root, "Cancelled", "Delete cancelled.", "info")
            return
        try:
            success = delete_student(int(roll_no), branch)
            if success:
                ModernDialog(self.root, "Deleted", "🗑 Student record deleted.", "success")
                self.load_data()
            else:
                ModernDialog(self.root, "Error", "❌ Could not delete student.", "error")
        except Exception as e:
            ModernDialog(self.root, "Error", f"⚠ {str(e)}", "error")

    # ------------------ Algorithm Features ------------------
    def sort_data(self):
        students = fetch_all_students()
        sorted_students = merge_sort(students, key_index=3)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in sorted_students:
            tag = "debarred" if s[4] < 75 else ""
            self.tree.insert("", "end", values=s, tags=(tag,))
        self.tree.tag_configure("debarred", foreground="#FF4D4D", background="#3B0000")
        ModernDialog(self.root, "Merge Sort", "✅ Students sorted by marks.", "info")

    def search_data(self):
        prompts = [("Binary Search", "Enter Roll No to search:", "int")]
        vals = self.ask_sequence_inputs(prompts)
        if vals is None:
            return
        roll_no = vals[0]
        students = fetch_all_students()
        students.sort(key=lambda x: x[0])
        result = binary_search(students, int(roll_no))
        if result:
            ModernDialog(self.root, "Found", f"🎯 {result[1]} ({result[2]})\nMarks: {result[3]}, Attendance: {result[4]}", "success")
        else:
            ModernDialog(self.root, "Not Found", "No student with that roll number found.", "warning")

        # ------------------ Summary & Graphs ------------------

        # ------------------ Summary & Graphs ------------------

    def show_summary(self):
        students = fetch_all_students()
        if not students:
            ModernDialog(self.root, "No Data", "No records found to summarize.", "warning")
            return

        branches = {}
        debarred = 0
        for s in students:
            branch = s[2].upper()
            if branch not in branches:
                branches[branch] = {"marks": [], "attendance": []}
            branches[branch]["marks"].append(s[3])
            branches[branch]["attendance"].append(s[4])
            if s[4] < 75:
                debarred += 1

        # --- Create popup window ---
        summary_win = ctk.CTkToplevel(self.root)
        summary_win.title("Summary Statistics")
        summary_win.configure(fg_color="#1E1E1E")
        summary_win.geometry("820x720")

        # Bring window to front and make modal
        summary_win.transient(self.root)
        summary_win.grab_set()
        summary_win.lift()
        summary_win.focus_force()
        center_window(summary_win, self.root, 820, 720)

        # ---------------- Header ----------------
        ctk.CTkLabel(
            summary_win,
            text="📈 Branch Summary Statistics",
            font=("Helvetica", 20, "bold"),
            text_color="#F8F9FA"
        ).pack(pady=(20, 10))

        # ---------------- Scrollable Frame ----------------
        scroll_frame = ctk.CTkScrollableFrame(
            summary_win, width=780, height=580, fg_color="#2B2B2B"
        )
        scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # ---------------- Summary Text Formatting ----------------
        summary_text = ""
        for branch, vals in branches.items():
            m = np.array(vals["marks"])
            a = np.array(vals["attendance"])
            summary_text += (
                f"───────────────────────────────\n"
                f"📘 {branch} BRANCH\n"
                f"───────────────────────────────\n"
                f"• Average Marks:      {m.mean():.2f}\n"
                f"• Maximum Marks:      {m.max():.2f}\n"
                f"• Minimum Marks:      {m.min():.2f}\n"
                f"• Average Attendance: {a.mean():.2f}%\n"
                f"• Maximum Attendance: {a.max():.2f}%\n"
                f"• Minimum Attendance: {a.min():.2f}%\n\n"
            )

        summary_text += f"🚫 Total Debarred Students (Attendance < 75%): {debarred}\n"

        box = ctk.CTkTextbox(scroll_frame, width=440, height=220)
        box.pack(pady=(5, 20))
        box.insert("1.0", summary_text.strip())
        box.configure(state="disabled")

        # ---------------- Matplotlib Graphs ----------------
        fig, axs = plt.subplots(2, 1, figsize=(8, 8), facecolor="#1E1E1E")
        fig.subplots_adjust(hspace=0.45)

        # --- Line Graph: Marks Trend per Branch ---
        for branch, vals in branches.items():
            marks_sorted = sorted(vals["marks"])
            axs[0].plot(
                range(1, len(marks_sorted) + 1),
                marks_sorted,
                marker="o",
                linewidth=2,
                label=branch
            )
        axs[0].set_title("Marks Trend per Branch", color="white", fontsize=12)
        axs[0].set_xlabel("Students (sorted by marks)", color="white")
        axs[0].set_ylabel("Marks", color="white")
        axs[0].set_facecolor("#2C2C2C")
        axs[0].tick_params(colors="white")
        axs[0].xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ymin, ymax = axs[0].get_ylim()
        axs[0].set_ylim(ymin, ymax + 5)
        axs[0].legend(facecolor="#1E1E1E", edgecolor="white", labelcolor="white")

        # --- Scatter Graph: Marks vs Attendance ---
        for branch, vals in branches.items():
            axs[1].scatter(vals["marks"], vals["attendance"], label=branch)
        axs[1].set_title("Marks vs Attendance", color="white", fontsize=12)
        axs[1].set_xlabel("Marks", color="white")
        axs[1].set_ylabel("Attendance (%)", color="white")
        axs[1].set_facecolor("#2C2C2C")
        axs[1].tick_params(colors="white")
        axs[1].legend(facecolor="#1E1E1E", edgecolor="white", labelcolor="white")

        canvas = FigureCanvasTkAgg(fig, master=scroll_frame)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(pady=10)

        # ---------------- Close Handler ----------------
        def on_close():
            try:
                canvas.get_tk_widget().destroy()
                plt.close(fig)
            except Exception:
                pass
            summary_win.destroy()

        summary_win.protocol("WM_DELETE_WINDOW", on_close)

        ctk.CTkButton(
            summary_win,
            text="Close",
            width=120,
            fg_color="#0D6EFD",
            command=on_close
        ).pack(pady=15)


def center_main_window(win, width=950, height=600):
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = ctk.CTk()
    center_main_window(root) 
    app = StudentDashboard(root)
    root.mainloop()
