import pytest
from src.utils import dependency_manager
from src.utils.dependency_manager import auto_import
import importlib
import sys
from unittest.mock import patch, MagicMock

def test_auto_import_existing():
    # Test importing a standard library module that definitely exists
    os_module = auto_import("os")
    assert os_module.__name__ == "os"

def test_auto_import_custom_name():
    # Test with a specific import name
    # We'll use 'multipart' for 'python-multipart' logic check
    with patch("importlib.import_module") as mock_import:
        mock_import.return_value = MagicMock()
        auto_import("python-multipart")
        mock_import.assert_called_with("multipart")

@patch("subprocess.check_call")
@patch("shutil.which")
def test_auto_import_install_logic(mock_which, mock_check_call):
    # Test the installation logic when import fails
    mock_which.return_value = None # Not a UV environment
    
    # We want importlib to fail the first time, then succeed
    with patch("importlib.import_module") as mock_import:
        mock_import.side_effect = [ImportError, MagicMock()]
        
        # We need to mock _ensure_pip to avoid real subprocess calls
        with patch.object(dependency_manager, "_ensure_pip") as mock_ensure:
            auto_import("fake-package")
            
            # Verify pip install was called
            mock_check_call.assert_called()
            assert "pip" in mock_check_call.call_args[0][0]

@patch("subprocess.check_call")
@patch("shutil.which")
def test_auto_import_uv_logic(mock_which, mock_check_call):
    # Test UV detection
    mock_which.return_value = "/usr/local/bin/uv"
    
    with patch("importlib.import_module") as mock_import:
        mock_import.side_effect = [ImportError, MagicMock()]
        auto_import("another-fake-package")
        
        # Verify uv pip install was called
        mock_check_call.assert_called()
        assert "uv" in mock_check_call.call_args[0][0]
        assert "pip" in mock_check_call.call_args[0][0]
