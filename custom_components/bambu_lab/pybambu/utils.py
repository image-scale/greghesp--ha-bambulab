"""
Utility functions for PyBambu library
"""
import json
import os

# Load error text data
_error_text_path = os.path.join(os.path.dirname(__file__), 'error_text.json')
with open(_error_text_path, 'r', encoding='utf-8') as f:
    _error_data = json.load(f)


def safe_json_loads(raw_bytes):
    """Safely load JSON from bytes"""
    if isinstance(raw_bytes, bytes):
        raw_bytes = raw_bytes.decode('utf-8')
    return json.loads(raw_bytes)


def _normalize_error_code(error_code):
    """Normalize error code to the standard format (XXXX_XXXX or XXXX_XXXX_XXXX_XXXX)"""
    # Remove any existing underscores and make uppercase
    code = error_code.upper().replace("_", "")

    if len(code) == 8:
        # Format: XXXXXXXX -> XXXX_XXXX
        return f"{code[:4]}_{code[4:]}"
    elif len(code) == 16:
        # Format: XXXXXXXXXXXXXXXX -> XXXX_XXXX_XXXX_XXXX
        return f"{code[:4]}_{code[4:8]}_{code[8:12]}_{code[12:]}"
    else:
        # Unknown format, return as-is with underscores
        return error_code.upper()


def _get_base_language(language):
    """Get the base language from a locale (e.g., 'de-CH' -> 'de')"""
    if '-' in language:
        return language.split('-')[0]
    return language


def _lookup_error_text(errors_dict, error_code, printer_model, language):
    """Look up error text with fallbacks for model and language"""
    code = _normalize_error_code(error_code)

    if code not in errors_dict:
        return "unknown"

    error_entry = errors_dict[code]

    # Try to find text in order of priority:
    # 1. Exact printer model + exact language
    # 2. Exact printer model + base language
    # 3. Exact printer model + English fallback
    # 4. Fallback models (same priority)
    # 5. _all + exact language
    # 6. _all + base language
    # 7. _all + English
    # 8. "unknown"

    base_lang = _get_base_language(language)
    model_fallbacks = _error_data.get("_model_fallback", {}).get(printer_model, [])
    models_to_try = [printer_model] + model_fallbacks + ["_all"]

    for model in models_to_try:
        if model in error_entry and isinstance(error_entry[model], dict):
            model_entry = error_entry[model]
            # Try exact language
            if language in model_entry:
                text = model_entry[language]
                if text:  # Skip empty strings
                    return text
            # Try base language
            if base_lang != language and base_lang in model_entry:
                text = model_entry[base_lang]
                if text:
                    return text
            # Try English fallback
            if "en" in model_entry and language != "en" and base_lang != "en":
                text = model_entry["en"]
                if text:
                    return text

    return "unknown"


def _get_severity(errors_dict, error_code):
    """Get the severity for an error code"""
    code = _normalize_error_code(error_code)

    if code not in errors_dict:
        return "unknown"

    error_entry = errors_dict[code]
    return error_entry.get("_severity", "unknown")


def get_HMS_error_text(error_code, printer_model, language):
    """Get HMS error text for a given error code, printer model, and language"""
    return _lookup_error_text(_error_data.get("hms", {}), error_code, printer_model, language)


def get_print_error_text(error_code, printer_model, language):
    """Get print error text for a given error code, printer model, and language"""
    return _lookup_error_text(_error_data.get("print", {}), error_code, printer_model, language)


def get_HMS_severity(error_code):
    """Get HMS error severity for a given error code"""
    return _get_severity(_error_data.get("hms", {}), error_code)
