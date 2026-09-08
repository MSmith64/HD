"""Convenience launcher. Normal hosting uses Streamlit + requirements.txt."""
from __future__ import annotations
import importlib.util, subprocess, sys

REQUIRED = {"streamlit": "streamlit>=1.40,<2", "fitz": "PyMuPDF>=1.24", "timezonefinder": "timezonefinder>=6.5", "geopy": "geopy>=2.4", "swisseph": "pyswisseph>=2.10"}
missing=[spec for mod,spec in REQUIRED.items() if importlib.util.find_spec(mod) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
subprocess.check_call([sys.executable, "-m", "streamlit", "run", "app.py"])
