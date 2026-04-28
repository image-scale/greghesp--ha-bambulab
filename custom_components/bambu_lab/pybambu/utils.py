"""
Utility functions for PyBambu library
"""
import json


def safe_json_loads(raw_bytes):
    """Safely load JSON from bytes"""
    raise NotImplementedError


def get_HMS_error_text(error_code, printer_model, language):
    """Get HMS error text for a given error code, printer model, and language"""
    raise NotImplementedError


def get_print_error_text(error_code, printer_model, language):
    """Get print error text for a given error code, printer model, and language"""
    raise NotImplementedError
