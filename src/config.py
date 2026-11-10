#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
config.py: Gestión de configuración para KDuck (Auto-Ducking Inteligente).
"""

import os
import tomllib
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path.home() / ".config/kduck"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG_TOML = """# Configuración de KDuck: Auto-Ducking Inteligente para PipeWire & WirePlumber 0.5

[ducking]
# Nivel de volumen al atenuar (porcentaje del volumen original, ej. 20 = 20%)
duck_volume_percent = 20

# Duración de las transiciones suaves en milisegundos
attack_ramp_ms = 350
release_ramp_ms = 500

# Pausar reproductores multimedia activos (MPRIS) durante llamadas
pause_mpris_on_calls = true

# Disparadores automáticos
trigger_on_comm_streams = true
trigger_on_kdeconnect_call = true

# Clientes o nodos de audio ignorados
ignore_clients = ["kwin_wayland", "libcanberra", "easyeffects"]
"""


def ensure_config_exists() -> Path:
    """Asegura que el directorio y archivo de configuración existan."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONFIG_TOML)
    return CONFIG_FILE


def load_config(config_path: Path = None) -> Dict[str, Any]:
    """Carga y valida la configuración desde el archivo TOML."""
    target = config_path if config_path else ensure_config_exists()
    if not target.is_file():
        return {}

    with open(target, "rb") as f:
        try:
            data = tomllib.load(f)
            return data.get("ducking", {})
        except Exception as exc:
            print(f"Error al leer configuración de {target}: {exc}")
            return {}
