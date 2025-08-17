import os
import sys
import datetime
import threading
import time

from pynput import keyboard, mouse
import psycopg2
import psutil
import pygetwindow as gw # For getting window titles (Windows/macOS)

# --- Database & Employee Configuration ---
# IMPORTANT: These will be set via environment variables when you run the script.
# Default values for local testing (matches Docker Compose setup if run on same PC)
DB_HOST = os.getenv("PG_HOST", "localhost")  # Use 'localhost' as Docker Desktop maps ports
DB_PORT = os.getenv("PG_PORT", "5433")      # Mapped port for ai_log_db service
DB_NAME = os.getenv("PG_DB", "ai_logs")
DB_USER = os.getenv("PG_USER", "ai_app_user")
DB_PASSWORD = os.getenv("PG_PASSWORD", "supersecret_dev_pass")
EMPLOYEE_ID = os.getenv("EMPLOYEE_ID", os.environ.get("USERNAME", "unknown_windows_user")) # Auto-detect Windows username

# Global variable to store active window info
current_active_window = {"app": "Unknown", "title": "Unknown"}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def log_activity_to_db(event_type, application_name, window_title, event_detail, employee_id=EMPLOYEE_ID):
    """Inserts a new activity log into the database."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employee_system_activity (employee_id, event_type, application_name, window_title, event_detail)
                VALUES (%s, %s, %s, %s, %s)
            """, (employee_id, event_type, application_name, window_title, event_detail))
        conn.commit()
    except Exception as e:
        print(f"Error logging activity to DB: {e}")
    finally:
        if conn:
            conn.close()

def update_active_window():
    """Periodically updates the active window information."""
    global current_active_window
    while True:
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                app_name = "Unknown"
                try:
                    proc = psutil.Process(active_window.pid)
                    app_name = proc.name()
                except (psutil.NoSuchProcess, AttributeError):
                    pass

                if current_active_window["app"] != app_name or current_active_window["title"] != active_window.title:
                    current_active_window["app"] = app_name
                    current_active_window["title"] = active_window.title
                    print(f"Active App Changed: {app_name} - {active_window.title}")
                    log_activity_to_db(
                        event_type="app_focus",
                        application_name=app_name,
                        window_title=active_window.title,
                        event_detail=f"Focused on {app_name} - {active_window.title}"
                    )
            else:
                if current_active_window["app"] != "Desktop" or current_active_window["title"] != "Desktop":
                    current_active_window["app"] = "Desktop"
                    current_active_window["title"] = "Desktop"
                    log_activity_to_db(
                        event_type="app_focus",
                        application_name="Desktop",
                        window_title="Desktop",
                        event_detail="Focused on Desktop"
                    )
        except Exception as e:
             pass # Ignore errors if window info cannot be retrieved (e.g., non-gui env)
        time.sleep(5) # Check every 5 seconds

def on_key_press(key):
    """Callback for keyboard press events."""
    try:
        key_char = str(key).replace("'", "")
        if key == keyboard.Key.space:
            key_char = "[SPACE]"
        elif key == keyboard.Key.enter:
            key_char = "[ENTER]"
        elif key == keyboard.Key.backspace:
            key_char = "[BACKSPACE]"
        elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            key_char = "[SHIFT]"
        elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
            key_char = "[ALT]"
        elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
            key_char = "[CTRL]"
        elif key == keyboard.Key.tab:
            key_char = "[TAB]"
        elif key == keyboard.Key.esc:
            key_char = "[ESC]"
        elif hasattr(key, 'char'):
            key_char = key.char
        else:
            key_char = f"[{key.name.upper()}]"

        log_activity_to_db(
            event_type="keyboard",
            application_name=current_active_window["app"],
            window_title=current_active_window["title"],
            event_detail=f"Key: {key_char}"
        )
    except Exception as e:
        print(f"Error in on_key_press: {e}")

def on_mouse_click(x, y, button, pressed):
    """Callback for mouse click events."""
    if pressed:
        log_activity_to_db(
            event_type="mouse_click",
            application_name=current_active_window["app"],
            window_title=current_active_window["title"],
            event_detail=f"Click: {button.name} at X={x}, Y={y}"
        )

def main():
    print("Starting Employee Activity Logger...")
    print(f"Logging for Employee ID: {EMPLOYEE_ID}")
    print(f"Connecting to DB: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    window_thread = threading.Thread(target=update_active_window, daemon=True)
    window_thread.start()

    with keyboard.Listener(on_press=on_key_press) as k_listener, \
         mouse.Listener(on_click=on_mouse_click) as m_listener:
        print("Listening for keyboard and mouse events. Press Ctrl+C to stop...")
        try:
            k_listener.join()
            m_listener.join()
        except KeyboardInterrupt:
            print("\nStopping logger...")
        except Exception as e:
            print(f"An error occurred in a listener: {e}")

if __name__ == "__main__":
    main()