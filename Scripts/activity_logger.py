# activity_logger.py (Run this on your local PC, outside the Docker project folder)

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
                INSERT INTO employee_system_activity (employee_id, timestamp, event_type, application_name, window_title, event_detail)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (employee_id, datetime.datetime.now(), event_type, application_name, window_title, event_detail))
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
            if active_window and active_window.title:
                app_name = "Unknown"
                try:
                    proc = psutil.Process(active_window.pid)
                    if sys.platform == "win32":
                        # Use exe name on Windows for better accuracy
                        if hasattr(active_window, '_hWnd') and active_window._hWnd:
                             app_name = proc.name() # Fallback to psutil name
                    else:
                        app_name = proc.name()
                except (psutil.NoSuchProcess, AttributeError, PermissionError):
                    # Fallback for system processes or when permissions are denied
                    pass

                # Check if the focused window has changed
                if current_active_window["app"] != app_name or current_active_window["title"] != active_window.title:
                    current_active_window["app"] = app_name
                    current_active_window["title"] = active_window.title
                    log_activity_to_db(
                        event_type="app_focus",
                        application_name=app_name,
                        window_title=active_window.title,
                        event_detail=f"Focused on app '{app_name}' with title '{active_window.title}'"
                    )
            else: # No active window (e.g., desktop)
                if current_active_window["title"] != "Desktop":
                    current_active_window["app"] = "Desktop"
                    current_active_window["title"] = "Desktop"
                    log_activity_to_db(
                        event_type="app_focus",
                        application_name="Desktop",
                        window_title="Desktop",
                        event_detail="Focused on Desktop"
                    )
        except Exception as e:
             pass # Ignore errors if window info cannot be retrieved
        time.sleep(5)

def on_key_press(key):
    """Callback for keyboard press events."""
    try:
        key_char = ""
        if hasattr(key, 'char') and key.char is not None:
            key_char = key.char
        else:
            # Handle special keys
            key_map = {
                keyboard.Key.space: "[SPACE]", keyboard.Key.enter: "[ENTER]",
                keyboard.Key.backspace: "[BACKSPACE]", keyboard.Key.shift: "[SHIFT]",
                keyboard.Key.ctrl: "[CTRL]", keyboard.Key.alt: "[ALT]",
                keyboard.Key.tab: "[TAB]", keyboard.Key.esc: "[ESC]"
            }
            key_char = key_map.get(key, f"[{key.name.upper()}]" if hasattr(key, 'name') else "[UNKNOWN_KEY]")

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
# activity_logger.py (Run this on your local PC, outside the Docker project folder)

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
                INSERT INTO employee_system_activity (employee_id, timestamp, event_type, application_name, window_title, event_detail)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (employee_id, datetime.datetime.now(), event_type, application_name, window_title, event_detail))
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
            if active_window and active_window.title:
                app_name = "Unknown"
                try:
                    proc = psutil.Process(active_window.pid)
                    if sys.platform == "win32":
                        # Use exe name on Windows for better accuracy
                        if hasattr(active_window, '_hWnd') and active_window._hWnd:
                             app_name = proc.name() # Fallback to psutil name
                    else:
                        app_name = proc.name()
                except (psutil.NoSuchProcess, AttributeError, PermissionError):
                    # Fallback for system processes or when permissions are denied
                    pass

                # Check if the focused window has changed
                if current_active_window["app"] != app_name or current_active_window["title"] != active_window.title:
                    current_active_window["app"] = app_name
                    current_active_window["title"] = active_window.title
                    log_activity_to_db(
                        event_type="app_focus",
                        application_name=app_name,
                        window_title=active_window.title,
                        event_detail=f"Focused on app '{app_name}' with title '{active_window.title}'"
                    )
            else: # No active window (e.g., desktop)
                if current_active_window["title"] != "Desktop":
                    current_active_window["app"] = "Desktop"
                    current_active_window["title"] = "Desktop"
                    log_activity_to_db(
                        event_type="app_focus",
                        application_name="Desktop",
                        window_title="Desktop",
                        event_detail="Focused on Desktop"
                    )
        except Exception as e:
             pass # Ignore errors if window info cannot be retrieved
        time.sleep(5)

def on_key_press(key):
    """Callback for keyboard press events."""
    try:
        key_char = ""
        if hasattr(key, 'char') and key.char is not None:
            key_char = key.char
        else:
            # Handle special keys
            key_map = {
                keyboard.Key.space: "[SPACE]", keyboard.Key.enter: "[ENTER]",
                keyboard.Key.backspace: "[BACKSPACE]", keyboard.Key.shift: "[SHIFT]",
                keyboard.Key.ctrl: "[CTRL]", keyboard.Key.alt: "[ALT]",
                keyboard.Key.tab: "[TAB]", keyboard.Key.esc: "[ESC]"
            }
            key_char = key_map.get(key, f"[{key.name.upper()}]" if hasattr(key, 'name') else "[UNKNOWN_KEY]")

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
# activity_logger.py (Run this on your local PC, outside the Docker project folder)

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
                INSERT INTO employee_system_activity (employee_id, timestamp, event_type, application_name, window_title, event_detail)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (employee_id, datetime.datetime.now(), event_type, application_name, window_title, event_detail))
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
            if active_window and active_window.title:
                app_name = "Unknown"
                try:
                    proc = psutil.Process(active_window.pid)
                    if sys.platform == "win32":
                        # Use exe name on Windows for better accuracy
                        if hasattr(active_window, '_hWnd') and active_window._hWnd:
                             app_name = proc.name() # Fallback to psutil name
                    else:
                        app_name = proc.name()
                except (psutil.NoSuchProcess, AttributeError, PermissionError):
                    # Fallback for system processes or when permissions are denied
                    pass

                # Check if the focused window has changed
                if current_active_window["app"] != app_name or current_active_window["title"] != active_window.title:
                    current_active_window["app"] = app_name
                    current_active_window["title"] = active_window.title
                    log_activity_to_db(
                        event_type="app_focus",
                        application_name=app_name,
                        window_title=active_window.title,
                        event_detail=f"Focused on app '{app_name}' with title '{active_window.title}'"
                    )
            else: # No active window (e.g., desktop)
                if current_active_window["title"] != "Desktop":
                    current_active_window["app"] = "Desktop"
                    current_active_window["title"] = "Desktop"
                    log_activity_to_db(
                        event_type="app_focus",
                        application_name="Desktop",
                        window_title="Desktop",
                        event_detail="Focused on Desktop"
                    )
        except Exception as e:
             pass # Ignore errors if window info cannot be retrieved
        time.sleep(5)

def on_key_press(key):
    """Callback for keyboard press events."""
    try:
        key_char = ""
        if hasattr(key, 'char') and key.char is not None:
            key_char = key.char
        else:
            # Handle special keys
            key_map = {
                keyboard.Key.space: "[SPACE]", keyboard.Key.enter: "[ENTER]",
                keyboard.Key.backspace: "[BACKSPACE]", keyboard.Key.shift: "[SHIFT]",
                keyboard.Key.ctrl: "[CTRL]", keyboard.Key.alt: "[ALT]",
                keyboard.Key.tab: "[TAB]", keyboard.Key.esc: "[ESC]"
            }
            key_char = key_map.get(key, f"[{key.name.upper()}]" if hasattr(key, 'name') else "[UNKNOWN_KEY]")

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
