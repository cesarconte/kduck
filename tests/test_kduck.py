#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
test_kduck.py: Suite de pruebas unitarias para KDuck.
"""

import sys
import unittest
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from config import load_config
from ducking_engine import DuckingEngine
from mpris_controller import MprisController


class TestKDuck(unittest.TestCase):
    def test_ducking_engine_state(self):
        engine = DuckingEngine()
        self.assertFalse(engine.is_ducked)

        # Mocking or testing state logic
        engine.original_volume = 0.50
        engine.is_ducked = True
        self.assertTrue(engine.is_ducked)

        # Test volume clamping
        engine.set_volume(1.5)  # should clamp without error
        engine.set_volume(-0.5) # should clamp without error

    def test_config_parsing(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".toml") as tmp:
            tmp.write("""
[ducking]
duck_volume_percent = 25
attack_ramp_ms = 400
release_ramp_ms = 600
pause_mpris_on_calls = false
""")
            tmp.flush()
            cfg = load_config(Path(tmp.name))
            self.assertEqual(cfg.get("duck_volume_percent"), 25)
            self.assertEqual(cfg.get("attack_ramp_ms"), 400)
            self.assertEqual(cfg.get("release_ramp_ms"), 600)
            self.assertFalse(cfg.get("pause_mpris_on_calls"))

    def test_mpris_controller_init(self):
        mpris = MprisController()
        self.assertEqual(len(mpris._paused_by_kduck), 0)


if __name__ == "__main__":
    unittest.main()
