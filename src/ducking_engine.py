#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
ducking_engine.py: Motor de cálculo de rampas y control de volumen para KDuck.
"""

import time
import subprocess
import threading
from typing import Optional


class DuckingEngine:
    def __init__(self, target_sink: str = "@DEFAULT_AUDIO_SINK@"):
        self.target_sink = target_sink
        self.is_ducked = False
        self.original_volume: Optional[float] = None
        self._lock = threading.Lock()
        self._ramp_thread: Optional[threading.Thread] = None
        self._cancel_ramp = False

    def get_current_volume(self) -> float:
        """Obtiene el volumen actual del sink de audio objetivo."""
        try:
            res = subprocess.run(
                ["wpctl", "get-volume", self.target_sink],
                capture_output=True, text=True, check=True
            )
            # Formato típico: "Volume: 0.42" o "Volume: 0.42 [MUTED]"
            parts = res.stdout.strip().split()
            if len(parts) >= 2 and parts[0] == "Volume:":
                return float(parts[1])
        except Exception as exc:
            print(f"Error al leer volumen de {self.target_sink}: {exc}")
        return 0.50

    def set_volume(self, volume: float):
        """Establece el volumen de forma inmediata en wpctl."""
        clamped = max(0.0, min(1.0, round(volume, 3)))
        try:
            subprocess.run(
                ["wpctl", "set-volume", self.target_sink, f"{clamped:.3f}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
            )
        except Exception:
            pass

    def _execute_ramp(self, start_vol: float, end_vol: float, duration_ms: int):
        """Ejecuta una rampa de volumen suave en N pasos temporizados."""
        steps = max(5, int(duration_ms / 30)) # Pasos de aprox 30ms
        step_delay = (duration_ms / 1000.0) / steps
        vol_step = (end_vol - start_vol) / steps

        current = start_vol
        for _ in range(steps):
            if self._cancel_ramp:
                break
            current += vol_step
            self.set_volume(current)
            time.sleep(step_delay)

        if not self._cancel_ramp:
            self.set_volume(end_vol)

    def start_ducking(self, duck_percent: int = 20, attack_ms: int = 350):
        """Inicia la atenuación hacia el porcentaje objetivo con rampa de ataque."""
        with self._lock:
            if self.is_ducked:
                return

            current_vol = self.get_current_volume()
            self.original_volume = current_vol

            target_vol = max(0.05, current_vol * (duck_percent / 100.0))
            self._cancel_ramp = False
            self.is_ducked = True

            print(f"📉 [KDuck] Atenuando audio: {int(current_vol*100)}% -> {int(target_vol*100)}% ({attack_ms}ms)")
            self._ramp_thread = threading.Thread(
                target=self._execute_ramp,
                args=(current_vol, target_vol, attack_ms),
                daemon=True
            )
            self._ramp_thread.start()

    def stop_ducking(self, release_ms: int = 500):
        """Restaura el volumen original con rampa de liberación."""
        with self._lock:
            if not self.is_ducked or self.original_volume is None:
                return

            current_vol = self.get_current_volume()
            target_vol = self.original_volume
            self._cancel_ramp = False

            print(f"📈 [KDuck] Restaurando audio: {int(current_vol*100)}% -> {int(target_vol*100)}% ({release_ms}ms)")
            self._ramp_thread = threading.Thread(
                target=self._execute_ramp,
                args=(current_vol, target_vol, release_ms),
                daemon=True
            )
            self._ramp_thread.start()
            self.is_ducked = False

    def reset_on_exit(self):
        """Restaura el volumen inmediatamente si el proceso termina de forma abrupta."""
        if self.is_ducked and self.original_volume is not None:
            self.set_volume(self.original_volume)
