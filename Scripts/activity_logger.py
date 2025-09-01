# activity_logger.py (IMPROVED APP NAME DETECTION)
import os
import sys
import datetime
import threading
import time

from pynput import keyboard, mouse
import psycopg2
import psutil
import pygetwindow as gw

# --- Database & Employee Configuration ---
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5433")
DB_NAME = os.getenv("PG_DB", "ai_logs")
DB_USER = os.getenv("PG_USER", "karanesh")
DB_PASSWORD = os.getenv("PG_PASSWORD", "jaic0806")
EMPLOYEE_ID = os.getenv("EMPLOYEE_ID", os.environ.get("USERNAME", "unknown_windows_user"))

current_active_window = {"app": "Unknown", "title": "Unknown"}

def get_db_connection():
    # ... (this function remains the same)
    try:
        conn_string = (f"host='{DB_HOST}' port='{DB_PORT}' dbname='{DB_NAME}' "
                       f"user='{DB_USER}' password='{DB_PASSWORD}' sslmode='disable'")
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def log_activity_to_db(event_type, application_name, window_title, event_detail):
    # ... (this function remains the same)
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employee_system_activity (employee_id, timestamp, event_type, application_name, window_title, event_detail)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (EMPLOYEE_ID, datetime.datetime.now(), event_type, application_name, window_title, event_detail))
        conn.commit()
    except Exception as e:
        print(f"Error logging activity to DB: {e}")
    finally:
        if conn: conn.close()

def update_active_window():
    global current_active_window
    while True:
        try:
            active_window = gw.getActiveWindow()
            if active_window and active_window.title:
                app_name = "Unknown"
                window_title = active_window.title
                try:
                    # --- IMPROVED LOGIC ---
                    # On Windows, psutil can get the .exe name directly
                    proc = psutil.Process(active_window._hWnd)
                    app_name = proc.name()
                except (psutil.NoSuchProcess, AttributeError, PermissionError):
                    # Fallback if process info fails
                    app_name = window_title.split(' - ')[-1] # Guess from title

                if current_active_window["title"] != window_title:
                    current_active_window["app"] = app_name
                    current_active_window["title"] = window_title
                    log_activity_to_db("app_focus", app_name, window_title, f"Focused on {app_name}")
            else:
                if current_active_window["title"] != "Desktop":
                    current_active_window["app"] = "Desktop"
                    current_active_window["title"] = "Desktop"
                    log_activity_to_db("app_focus", "Desktop", "Desktop", "Focused on Desktop")
        except Exception:
             pass
        time.sleep(3)

# ... (on_key_press, on_mouse_click, and main functions remain the same) ...
def on_key_press(key):
    log_activity_to_db("keyboard", current_active_window["app"], current_active_window["title"], "User is typing")
def on_mouse_click(x, y, button, pressed):
    if pressed: log_activity_to_db("mouse_click", current_active_window["app"], current_active_window["title"], "User clicked")
def main():
    print("Starting Logger...")
    window_thread = threading.Thread(target=update_active_window, daemon=True)
    window_thread.start()
    with keyboard.Listener(on_press=on_key_press) as k_listener, mouse.Listener(on_click=on_mouse_click) as m_listener:
        print("Listening... Press Ctrl+C to stop.")
        k_listener.join(); m_listener.join()

if __name__ == "__main__":
    main()