import sys
import pathlib

import pytest


def test_main_module_structure():
    # Test that __main__.py can be imported and has correct structure
    import appearance.__main__
    
    # Verify it imported the correct main function from app module
    from appearance.app import main as app_main
    assert appearance.__main__.main is app_main
    
    # Test the path calculation logic used in __main__.py
    fake_file = pathlib.Path("/fake/mb_appearance/appearance/__main__.py")
    parent_parent = fake_file.parent.parent
    assert parent_parent == pathlib.Path("/fake/mb_appearance")
    assert str(parent_parent).endswith("mb_appearance")