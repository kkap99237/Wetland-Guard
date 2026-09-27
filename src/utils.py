"""
src/utils.py
Utility helpers for serialization, checkpoint tracking, and formatting.
"""
import os
import json
import pandas as pd


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_risk_badge(category):
    if category == "HIGH":
        return "HIGH"
    elif category == "MEDIUM":
        return "MEDIUM"
    else:
        return "LOW"
