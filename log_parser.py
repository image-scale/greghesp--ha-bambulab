import re


def parse_log(log: str) -> dict[str, str]:
    """Parse unittest verbose output into per-test results.

    Args:
        log: Full stdout+stderr output of `bash run_test.sh 2>&1`.

    Returns:
        Dict mapping test_id to status.
        - test_id: unittest's native format (e.g. "pybambu.tests.test_models.TestHms.test_no_errors")
        - status: one of "PASSED", "FAILED", "SKIPPED", "ERROR"
    """
    results = {}

    # unittest verbose output has lines ending with " ... ok", " ... FAIL", " ... ERROR", " ... skipped ..."
    # The test id is in parentheses: test_name (module.Class.test_name)
    # Lines may span two lines when a docstring is present:
    #   test_name (module.Class.test_name)
    #   Docstring ... ok
    # Or single line:
    #   test_name (module.Class.test_name) ... ok

    # Match lines containing the test ID in parentheses
    # We need to pair test IDs with their results

    # Strategy: find all lines with " ... STATUS" and extract the test ID from the
    # preceding context. We'll scan for the pattern of "(dotted.test.id)" on the same
    # or previous line.

    lines = log.split('\n')

    # Track pending test id from a line with parentheses but no " ... " result
    pending_test_id = None

    for line in lines:
        stripped = line.rstrip()

        # Check if this line has a result marker
        result_match = re.search(r'\.\.\.\s+(ok|FAIL|ERROR|skipped(?:\s+.*)?)\s*$', stripped)

        if result_match:
            status_str = result_match.group(1)
            if status_str == 'ok':
                status = 'PASSED'
            elif status_str == 'FAIL':
                status = 'FAILED'
            elif status_str == 'ERROR':
                status = 'ERROR'
            elif status_str.startswith('skipped'):
                status = 'SKIPPED'
            else:
                continue

            # Try to extract test ID from this same line
            # Test IDs have at least 3 dotted segments: module.Class.test_method
            id_match = re.search(r'\(([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*){2,})\)', stripped)
            if id_match:
                test_id = id_match.group(1)
                results[test_id] = status
                pending_test_id = None
            elif pending_test_id:
                # The test ID was on the previous line
                results[pending_test_id] = status
                pending_test_id = None
        else:
            # Check if this line has a test ID but no result (docstring follows)
            id_match = re.match(r'^[\w]+\s+\(([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*){2,})\)\s*$', stripped)
            if id_match:
                pending_test_id = id_match.group(1)
            else:
                # Not a result line and not a test ID line — reset pending
                # (but only if not a docstring continuation)
                if pending_test_id and not stripped:
                    pending_test_id = None

    return results

