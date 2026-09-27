"""
tests/test_ui_encoding.py
Automated tests verifying that UI source files and headers maintain proper UTF-8 encoding
with zero replacement characters, no corrupted question marks, and valid UI theme tokens.
"""
import glob
import os
import pytest
from src.ui_theme import get_plotly_theme


def test_ui_files_utf8_and_no_corrupted_characters():
    """Verify that all UI Python files have clean UTF-8 encoding without replacement characters."""
    ui_files = ["app.py"] + glob.glob("pages/*.py") + ["src/ui_theme.py"]
    
    assert len(ui_files) >= 6
    
    for fpath in ui_files:
        assert os.path.exists(fpath), f"File {fpath} does not exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check that unicode replacement character does not exist
        assert "\ufffd" not in content, f"Replacement character found in {fpath}"
        assert "??" not in content, f"Double question mark corruption found in {fpath}"


def test_dashboard_title_em_dash():
    """Verify that 1_Dashboard.py contains the proper em-dash in its title."""
    dashboard_path = "pages/1_Dashboard.py"
    with open(dashboard_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "Wetland Guard — Regional Monitoring Map" in content
    assert "Wetland Guard ? Regional Monitoring Map" not in content


def test_plotly_theme_structure():
    """Verify that the enterprise Plotly theme has required structure."""
    theme = get_plotly_theme()
    assert isinstance(theme, dict)
    assert "font" in theme
    assert "paper_bgcolor" in theme
    assert "xaxis" in theme
    assert "yaxis" in theme
