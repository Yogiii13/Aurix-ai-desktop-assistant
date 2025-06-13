import threading
import time
from datetime import datetime, timedelta
import logging
import json
import os

logger = logging.getLogger(__name__)

class Reminder:
    def __init__(self, callback):
        self.reminders = []
        self.callback = callback
        self.thread = threading.Thread(target=self._check_reminders, daemon=True)
        self.thread.start()
        self.reminders_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                          "data", "reminders.json")
        self._load_reminders()

    def add_reminder(self, message, when):
        """
        Add a new reminder.
        
        :param message: The reminder message
        :param when: A datetime object or a string in the format "YYYY-MM-DD HH:MM:SS"
        """
        if isinstance(when, str):
            when = datetime.strptime(when, "%Y-%m-%d %H:%M:%S")
        
        self.reminders.append((message, when))
        logger.info(f"Added reminder: {message} at {when}")
        self.save_reminders()
        return f"Reminder set for {when.strftime('%Y-%m-%d %H:%M:%S')}: {message}"

    def get_reminders(self):
        """Return a list of all active reminders."""
        return [f"{r[1].strftime('%Y-%m-%d %H:%M:%S')}: {r[0]}" for r in self.reminders]

    def _check_reminders(self):
        while True:
            now = datetime.now()
            triggered = [r for r in self.reminders if r[1] <= now]
            
            for reminder in triggered:
                self.reminders.remove(reminder)
                self.callback(reminder[0])
                logger.info(f"Triggered reminder: {reminder[0]}")
            
            if triggered:
                self.save_reminders()
                
            time.sleep(1)

    def clear_reminders(self):
        """Clear all reminders."""
        count = len(self.reminders)
        self.reminders.clear()
        logger.info(f"Cleared {count} reminders")
        self.save_reminders()
        return f"Cleared {count} reminders"
        
    def save_reminders(self):
        """Save reminders to a JSON file."""
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(self.reminders_file), exist_ok=True)
            
            # Convert datetime objects to strings for JSON serialization
            serializable_reminders = [
                (msg, dt.strftime("%Y-%m-%d %H:%M:%S")) 
                for msg, dt in self.reminders
            ]
            
            with open(self.reminders_file, 'w') as f:
                json.dump(serializable_reminders, f)
                
            logger.debug(f"Saved {len(self.reminders)} reminders to {self.reminders_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save reminders: {e}")
            return False
            
    def _load_reminders(self):
        """Load reminders from a JSON file."""
        try:
            if os.path.exists(self.reminders_file):
                with open(self.reminders_file, 'r') as f:
                    saved_reminders = json.load(f)
                
                # Convert string dates back to datetime objects
                for msg, dt_str in saved_reminders:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    # Only add reminders that haven't passed yet
                    if dt > datetime.now():
                        self.reminders.append((msg, dt))
                
                logger.debug(f"Loaded {len(self.reminders)} reminders from {self.reminders_file}")
        except Exception as e:
            logger.error(f"Failed to load reminders: {e}")