import json
from datetime import datetime
from typing import List, Dict, Any

class TaskManager:
    def __init__(self, file_path: str = 'tasks.json'):
        self.file_path = file_path
        self.tasks = self.load_tasks()

    def load_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from JSON file"""
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_tasks(self) -> None:
        """Save tasks to JSON file"""
        with open(self.file_path, 'w') as file:
            json.dump(self.tasks, file, indent=4)

    def add_task(self, title: str, priority: str, due_date: str = None) -> None:
        """Add a new task"""
        task = {
            'id': len(self.tasks) + 1,
            'title': title,
            'priority': priority,
            'due_date': due_date,
            'completed': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID"""
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        self.save_tasks()

    def toggle_task_status(self, task_id: int) -> None:
        """Toggle task completion status"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = not task['completed']
                break
        self.save_tasks()

    def update_task(self, task_id: int, title: str = None, 
                   priority: str = None, due_date: str = None) -> None:
        """Update task details"""
        for task in self.tasks:
            if task['id'] == task_id:
                if title:
                    task['title'] = title
                if priority:
                    task['priority'] = priority
                if due_date:
                    task['due_date'] = due_date
                break
        self.save_tasks()

    def get_sorted_tasks(self, sort_by: str = 'priority') -> List[Dict[str, Any]]:
        """Get tasks sorted by priority or due date"""
        if sort_by == 'priority':
            priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
            return sorted(self.tasks, key=lambda x: (priority_order[x['priority']], x['title']))
        elif sort_by == 'due_date':
            return sorted(self.tasks, 
                        key=lambda x: datetime.strptime(x['due_date'], '%Y-%m-%d') 
                        if x['due_date'] else datetime.max)
        return self.tasks
