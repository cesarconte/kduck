#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
monitor.py: Monitor reactivo de baja latencia para flujos de audio y llamadas en KDuck.
"""

import time
import json
import select
import subprocess
from typing import Dict, Any, List

from ducking_engine import DuckingEngine
from mpris_controller import MprisController


class AudioMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine = DuckingEngine()
        self.mpris = MprisController()
        self.duck_percent = int(config.get("duck_volume_percent", 20))
        self.attack_ms = int(config.get("attack_ramp_ms", 350))
        self.release_ms = int(config.get("release_ramp_ms", 500))
        self.pause_mpris = bool(config.get("pause_mpris_on_calls", True))
        self.ignore_clients = config.get("ignore_clients", ["kwin_wayland", "libcanberra", "easyeffects", "pw-record", "pw-cat"])

    def is_communication_active(self) -> bool:
        """Comprueba si hay un flujo de comunicación o llamada activo en PipeWire."""
        try:
            raw = subprocess.check_output(["pw-dump", "Node"], stderr=subprocess.DEVNULL)
            nodes = json.loads(raw)
        except Exception:
            return False

        for node in nodes:
            info = node.get("info", {})
            props = info.get("props", {})
            state = info.get("state", "")
            media_role = props.get("media.role", "")
            app_name = props.get("application.name", "")
            node_name = props.get("node.name", "")

            # Ignorar clientes excluidos
            if any(ign in app_name or ign in node_name for ign in self.ignore_clients):
                continue

            # Detectar llamadas de voz, WebRTC, VoIP
            if state == "running":
                if media_role in ("Communication", "Voice", "Phone"):
                    return True

        return False

    def is_kdeconnect_call_active(self) -> bool:
        """Consulta el estado de llamada o ducking en KDE Connect mediante D-Bus."""
        try:
            import dbus
            bus = dbus.SessionBus()
            for name in bus.list_names():
                if "kdeconnect" in name:
                    try:
                        obj = bus.get_object(name, "/modules/kdeconnect/telephony")
                        # Telephony activo
                    except Exception:
                        pass
        except Exception:
            pass
        return False

    def run_loop(self, stop_flag: List[bool] = None):
        """Bucle de monitorización reactiva basada en eventos de PipeWire con select()."""
        print("🎧 KDuck activo: vigilando flujos de audio de PipeWire de forma reactiva...")
        last_comm_state = False

        # Iniciar suscripción a eventos de audio de PipeWire/PulseAudio
        proc = subprocess.Popen(
            ["pactl", "subscribe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        try:
            while stop_flag is None or not stop_flag[0]:
                # Bloquear de forma eficiente con select() hasta recibir un evento relevante o timeout de 3s
                r, _, _ = select.select([proc.stdout], [], [], 3.0)
                if r:
                    line = proc.stdout.readline()
                    # Solo nos interesan cambios en flujos de reproducción/grabación o servidores
                    if not any(token in line for token in ["sink-input", "source-output", "source #", "sink #"]):
                        continue

                comm_active = self.is_communication_active() or self.is_kdeconnect_call_active()

                if comm_active and not last_comm_state:
                    print("📞 [KDuck] Voz o llamada detectada -> Iniciando auto-ducking")
                    if self.pause_mpris:
                        self.mpris.pause_active_players()
                    self.engine.start_ducking(self.duck_percent, self.attack_ms)
                    last_comm_state = True

                elif not comm_active and last_comm_state:
                    print("✅ [KDuck] Comunicación finalizada -> Restaurando volumen")
                    self.engine.stop_ducking(self.release_ms)
                    if self.pause_mpris:
                        self.mpris.resume_players()
                    last_comm_state = False

        finally:
            proc.terminate()
            proc.wait()
            self.engine.reset_on_exit()
