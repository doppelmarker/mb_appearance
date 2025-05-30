import sys
import importlib

import pytest


def test_main_module_execution(monkeypatch):
    # Test that the __main__ module can be imported and works correctly
    # Create a simple stub for main function
    main_called = False
    def stub_main():
        nonlocal main_called
        main_called = True
    
    # Monkeypatch the main function
    monkeypatch.setattr("appearance.app.main", stub_main)
    
    # Import __main__ which should import main from app
    import appearance.__main__
    importlib.reload(appearance.__main__)
    
    # The import itself doesn't call main (only when __name__ == "__main__")
    # So we test that the import works and main is accessible
    assert hasattr(appearance.__main__, "main")
    assert appearance.__main__.main is stub_main


def test_path_insertion():
    # Import should add parent directory to sys.path
    # Save original path
    original_paths = [p for p in sys.path if "mb_appearance" in p]
    
    # Remove any existing paths that might interfere
    sys.path = [p for p in sys.path if "mb_appearance" not in p]
    
    # Import the module to trigger path insertion
    import appearance.__main__
    importlib.reload(appearance.__main__)
    
    # Check that the parent directory was added
    assert any("mb_appearance" in p for p in sys.path)
    
    # Restore original paths
    sys.path = [p for p in sys.path if "mb_appearance" not in p] + original_paths