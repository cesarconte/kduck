#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
ducking_engine.py: Motor de cálculo de rampas, persistencia de estado y control de volumen para KDuck.
"""

import os
import json
import time
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Any


def get_state_file() -> Path:
    """Devuelve la ruta del archivo de estado en tmpfs o caché de usuario."""
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
    if xdg_runtime and Path(xdg_runtime).is_dir():
        state_dir = Path(xdg_runtime) / "kduck"
    else:
        state_dir = Path.home() / ".cache" / "kduck"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "state.json"


class DuckingEngine:
    def __init__(self, target_sink: str = "@DEFAULT_AUDIO_SINK@"):
        self.target_sink = target_sink
        self.state_file = get_state_file()
        self._lock = threading.Lock()
        self._ramp_thread: Optional[threading.Thread] = None
        self._cancel_ramp = False

    def load_state(self) -> Dict[str, Any]:
        """Carga el estado persistente desde disco."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"is_ducked": False, "original_volume": None, "ducked_volume": None}

    def save_state(self, state: Dict[str, Any]):
        """Guarda el estado persistente en disco."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error al guardar estado de KDuck: {e}")

    def get_current_volume(self) -> float:
        """Obtiene el volumen actual del sink de audio objetivo desde wpctl."""
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
        duration_ms = max(50, duration_ms)
        steps = max(5, int(duration_ms / 35))
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

    def start_ducking(self, duck_percent: int = 20, attack_ms: int = 350, wait: bool = False) -> bool:
        """
        Inicia la atenuación hacia el porcentaje objetivo con rampa de ataque.
        duck_percent: Porcentaje objetivo (ej. 20 para atenuar al 20%).
        wait: Si True, bloquea hasta que la rampa termine (imprescindible en ejecuciones CLI).
        """
        with self._lock:
            state = self.load_state()
            current_vol = self.get_current_volume()

            # Si ya estaba atenuado, conservamos el original_volume previo
            if state.get("is_ducked") and state.get("original_volume") is not None:
                orig_vol = float(state["original_volume"])
            else:
                orig_vol = current_vol

            # Cálculo de volumen objetivo:
            # Si el usuario pide duck 20, el volumen objetivo es 0.20 (20%).
            # Si el volumen actual ya es menor o igual, bajamos a la mitad del actual o mínimo 0.05.
            target_vol_val = duck_percent / 100.0
            if current_vol <= target_vol_val:
                target_vol = max(0.05, round(current_vol * 0.5, 3))
            else:
                target_vol = round(target_vol_val, 3)

            self._cancel_ramp = False
            state["is_ducked"] = True
            state["original_volume"] = orig_vol
            state["ducked_volume"] = target_vol
            state["timestamp"] = time.time()
            self.save_state(state)

            print(f"📉 [KDuck] Atenuando audio: {int(current_vol * 100)}% -> {int(target_vol * 100)}% ({attack_ms}ms)")

            if wait:
                self._execute_ramp(current_vol, target_vol, attack_ms)
            else:
                self._ramp_thread = threading.Thread(
                    target=self._execute_ramp,
                    args=(current_vol, target_vol, attack_ms),
                    daemon=True
                )
                self._ramp_thread.start()

            return True

    def stop_ducking(self, release_ms: int = 500, wait: bool = False) -> bool:
        """
        Restaura el volumen original con rampa de liberación.
        wait: Si True, bloquea hasta que la rampa termine.
        """
        with self._lock:
            state = self.load_state()
            orig_vol = state.get("original_volume")

            if orig_vol is None:
                # Si no hay volumen original guardado, usar un valor predeterminado seguro
                orig_vol = 0.50

            orig_vol = float(orig_vol)
            current_vol = self.get_current_volume()
            self._cancel_ramp = False

            state["is_ducked"] = False
            state["original_volume"] = None
            state["ducked_volume"] = None
            state["timestamp"] = time.time()
            self.save_state(state)

            print(f"📈 [KDuck] Restaurando audio: {int(current_vol * 100)}% -> {int(orig_vol * 100)}% ({release_ms}ms)")

            if wait:
                self._execute_ramp(current_vol, orig_vol, release_ms)
            else:
                self._ramp_thread = threading.Thread(
                    target=self._execute_ramp,
                    args=(current_vol, orig_vol, release_ms),
                    daemon=True
                )
                self._ramp_thread.start()

            return True

    def reset_on_exit(self):
        """Restaura el volumen inmediatamente si el servicio termina."""
        state = self.load_state()
        if state.get("is_ducked") and state.get("original_volume") is not None:
            self.set_volume(float(state["original_volume"]))
            state["is_ducked"] = False
            self.save_state(state)
