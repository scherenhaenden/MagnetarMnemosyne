import sys
import os

# Add src to path so we can import our modules easily
# Using absolute path discovery to ensure it works from any execution context
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from utils.dependency_manager import auto_import

def main():
    print("--- Exam System Starting ---")
    
    # Dynamically load web dependencies
    print("Initializing Web Modules (this may take a moment on first run)...")
    try:
        auto_import("fastapi")
        auto_import("uvicorn")
        auto_import("websockets")
        auto_import("jinja2")
        auto_import("python-multipart") # Necessary for Form data in FastAPI
        print("Web modules ready.")
    except Exception as e:
        print(f"Error initializing web modules: {e}")
        return

    # Import and run the UI server
    try:
        from ui.server import run_ui
        run_ui()
    except ImportError as e:
        print(f"Error: Could not find UI server module. Make sure 'src' folder exists. {e}")
    except Exception as e:
        print(f"An error occurred while starting the server: {e}")

if __name__ == "__main__":
    main()
