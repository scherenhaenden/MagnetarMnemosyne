import subprocess
import sys
import importlib
import os
import shutil

def _is_uv_environment():
    """Checks if we are running in a UV-managed environment or if UV is available."""
    # Check if UV binary exists
    return shutil.which("uv") is not None

def _ensure_pip():
    """Attempts to ensure pip is installed in the current environment (for non-uv setups)."""
    try:
        import pip
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
            return True
        except:
            return False

def auto_import(package_name, import_name=None):
    """
    Attempts to import a module. If it fails, it tries to install it.
    
    :param package_name: The name of the package to install (e.g., 'python-multipart')
    :param import_name: The name used to import (e.g., 'python_multipart' or 'multipart')
    """
    # Special case for python-multipart: the import name is often 'multipart' 
    # but the package is 'python-multipart'
    if package_name == "python-multipart" and import_name is None:
        import_name = "multipart"
    
    if import_name is None:
        import_name = package_name.replace("-", "_")
        
    try:
        return importlib.import_module(import_name)
    except ImportError:
        print(f"Module '{import_name}' not found. Auto-healing: Attempting to install '{package_name}'...")
        
        try:
            if _is_uv_environment():
                # If using UV, we should ideally use 'uv pip install' or 'uv add'
                # but 'uv pip install' is the safest for direct runtime additions
                print("UV detected. Using 'uv pip install' for faster healing...")
                subprocess.check_call(["uv", "pip", "install", package_name])
            else:
                _ensure_pip()
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            
            print(f"Successfully installed '{package_name}'. Re-attempting import...")
            importlib.invalidate_caches()
            return importlib.import_module(import_name)
        except Exception as e:
            print(f"Failed to auto-heal '{package_name}': {e}")
            # Final fallback: try standard pip if UV failed
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                importlib.invalidate_caches()
                return importlib.import_module(import_name)
            except:
                raise ImportError(f"Could not auto-install {package_name}. Please check internet or environment.")

if __name__ == "__main__":
    pass
