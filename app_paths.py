"""Persistent portable settings beside the executable, never in its extraction folder."""
from pathlib import Path
import sys


def data_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent
