#!/bin/bash
set -eo pipefail

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export CI=true

cd /workspace/ha-bambulab

python3 -u - <<'PY'
import os
import sys
import unittest

import select  # noqa: F401 — pre-import stdlib select to avoid shadowing by custom_components/bambu_lab/select.py

repo_root = os.getcwd()
sys.path.insert(0, os.path.join(repo_root, "custom_components", "bambu_lab"))

suite = unittest.defaultTestLoader.discover(
    start_dir=os.path.join(repo_root, "custom_components", "bambu_lab", "pybambu", "tests"),
    pattern="test_*.py",
    top_level_dir=os.path.join(repo_root, "custom_components", "bambu_lab"),
)

result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
PY

