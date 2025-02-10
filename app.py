import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading
import time

from task_manager import TaskManager
from notification_manager import NotificationManager
from styles import COLORS, PRIORITY_COLORS, FONTS

class GateTaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GATE Exam Task Manager")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS['bg'])

        self.task_manager = TaskManager()
        self.notification_manager = NotificationManager()

        self.setup_gui()
        self.start_notification_checker()

    def setup_gui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Task Input Section
        self.setup_input_section()

        # Task List Section
        self.setup_task_list()

        # Load initial tasks
        self.refresh_task_list()

    def setup_input_section(self):
        # Task Input Frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Add New Task", padding="5")
        input_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Task Title
        ttk.Label(input_frame, text="Task Title:").grid(row=0, column=0, padx=5, pady=5)
        self.task_title = ttk.Entry(input_frame, width=40)
        self.task_title.grid(row=0, column=1, padx=5, pady=5)

        # Priority
        ttk.Label(input_frame, text="Priority:").grid(row=0, column=2, padx=5, pady=5)
        self.priority = ttk.Combobox(input_frame, values=['High', 'Medium', 'Low'], width=10)
        self.priority.set('Medium')
        self.priority.grid(row=0, column=3, padx=5, pady=5)

        # Due Date
        ttk.Label(input_frame, text="Due Date:").grid(row=0, column=4, padx=5, pady=5)
        self.due_date = DateEntry(input_frame, width=12, background=COLORS['primary'],
                                foreground='white', borderwidth=2)
        self.due_date.grid(row=0, column=5, padx=5, pady=5)

        # Add Button
        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(
            row=0, column=6, padx=5, pady=5)

    def setup_task_list(self):
        # Task List Frame
        list_frame = ttk.LabelFrame(self.main_frame, text="Tasks", padding="5")
        list_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Sorting options
        sort_frame = ttk.Frame(list_frame)
        sort_frame.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="priority")
        ttk.Radiobutton(sort_frame, text="Priority", variable=self.sort_var, 
                       value="priority", command=self.refresh_task_list).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sort_frame, text="Due Date", variable=self.sort_var, 
                       value="due_date", command=self.refresh_task_list).pack(side=tk.LEFT, padx=5)

        # Task list
        self.task_tree = ttk.Treeview(list_frame, columns=("Title", "Priority", "Due Date", "Status"),
                                    show="headings", height=15)
        
        self.task_tree.heading("Title", text="Title")
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Due Date", text="Due Date")
        self.task_tree.heading("Status", text="Status")

        self.task_tree.column("Title", width=300)
        self.task_tree.column("Priority", width=100)
        self.task_tree.column("Due Date", width=100)
        self.task_tree.column("Status", width=100)

        self.task_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        # Buttons Frame
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=2, column=0, pady=5)

        ttk.Button(button_frame, text="Toggle Status", 
                  command=self.toggle_task_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Task", 
                  command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Task", 
                  command=self.edit_task).pack(side=tk.LEFT, padx=5)

    def add_task(self):
        title = self.task_title.get().strip()
        if not title:
            messagebox.showerror("Error", "Task title cannot be empty!")
            return

        self.task_manager.add_task(
            title=title,
            priority=self.priority.get(),
            due_date=self.due_date.get_date().strftime('%Y-%m-%d')
        )
        
        self.task_title.delete(0, tk.END)
        self.priority.set('Medium')
        self.refresh_task_list()

    def refresh_task_list(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        tasks = self.task_manager.get_sorted_tasks(self.sort_var.get())
        
        for task in tasks:
            status = "Completed" if task['completed'] else "Pending"
            self.task_tree.insert("", tk.END, values=(
                task['title'],
                task['priority'],
                task['due_date'],
                status
            ), tags=(str(task['id']),))

            # Set row color based on priority
            self.task_tree.tag_configure(str(task['id']), 
                foreground=PRIORITY_COLORS[task['priority']])

    def toggle_task_status(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task!")
            return

        task_id = int(self.task_tree.item(selected[0])['tags'][0])
        self.task_manager.toggle_task_status(task_id)
        self.refresh_task_list()

    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task!")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            task_id = int(self.task_tree.item(selected[0])['tags'][0])
            self.task_manager.delete_task(task_id)
            self.refresh_task_list()

    def edit_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task!")
            return

        task_values = self.task_tree.item(selected[0])['values']
        task_id = int(self.task_tree.item(selected[0])['tags'][0])

        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("400x200")

        ttk.Label(edit_window, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        title_entry = ttk.Entry(edit_window, width=30)
        title_entry.insert(0, task_values[0])
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Priority:").grid(row=1, column=0, padx=5, pady=5)
        priority_combo = ttk.Combobox(edit_window, values=['High', 'Medium', 'Low'])
        priority_combo.set(task_values[1])
        priority_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Due Date:").grid(row=2, column=0, padx=5, pady=5)
        due_date_entry = DateEntry(edit_window, width=12)
        due_date_entry.set_date(datetime.strptime(task_values[2], '%Y-%m-%d'))
        due_date_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_changes():
            self.task_manager.update_task(
                task_id=task_id,
                title=title_entry.get(),
                priority=priority_combo.get(),
                due_date=due_date_entry.get_date().strftime('%Y-%m-%d')
            )
            self.refresh_task_list()
            edit_window.destroy()

        ttk.Button(edit_window, text="Save", command=save_changes).grid(
            row=3, column=0, columnspan=2, pady=20)

    def start_notification_checker(self):
        def check_notifications():
            while True:
                self.notification_manager.check_due_tasks(self.task_manager.tasks)
                time.sleep(3600)  # Check every hour

        notification_thread = threading.Thread(target=check_notifications, daemon=True)
        notification_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = GateTaskManagerApp(root)
    root.mainloop()
