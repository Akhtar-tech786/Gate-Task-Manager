from plyer import notification
from datetime import datetime, timedelta

class NotificationManager:
    @staticmethod
    def show_notification(title, message):
        """Show a desktop notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,  # Icon path if needed
                timeout=10
            )
        except Exception as e:
            print(f"Notification error: {e}")

    @staticmethod
    def check_due_tasks(tasks):
        """Check for tasks due within 24 hours"""
        now = datetime.now()
        for task in tasks:
            if task.get('due_date') and not task.get('completed'):
                due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
                time_diff = due_date - now
                
                if timedelta(0) <= time_diff <= timedelta(days=1):
                    NotificationManager.show_notification(
                        "Task Due Soon!",
                        f"Task '{task['title']}' is due {task['due_date']}"
                    )
