"""
Utility functions for PyBambu library
"""
import json


def safe_json_loads(raw_bytes):
    """Safely load JSON from bytes"""
    if isinstance(raw_bytes, bytes):
        raw_bytes = raw_bytes.decode('utf-8')
    return json.loads(raw_bytes)


def get_HMS_error_text(error_code, printer_model, language):
    """Get HMS error text for a given error code, printer model, and language"""
    raise NotImplementedError


def get_print_error_text(error_code, printer_model, language):
    """Get print error text for a given error code, printer model, and language"""
    raise NotImplementedError
