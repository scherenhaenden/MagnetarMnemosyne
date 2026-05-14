import subprocess
import sys
import os

def run_coverage():
    # Ensure dependencies for testing are present
    from src.utils.dependency_manager import auto_import
    auto_import("pytest")
    auto_import("pytest-cov")
    auto_import("httpx") # Required for TestClient

    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest", 
        "--cov=src", 
        "--cov-report=term-missing",
        "tests/"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)

if __name__ == "__main__":
    run_coverage()
