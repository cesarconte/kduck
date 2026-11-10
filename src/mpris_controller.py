#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
mpris_controller.py: Control inteligente de pausa/reanudación de reproductores multimedia MPRIS.
"""

from typing import List, Set


class MprisController:
    def __init__(self):
        self._paused_by_kduck: Set[str] = set()

    def _get_bus(self):
        try:
            import dbus
            return dbus.SessionBus()
        except Exception:
            return None

    def pause_active_players(self) -> List[str]:
        """Pausa los reproductores que estén actualmente en reproducción."""
        bus = self._get_bus()
        if not bus:
            return []

        paused = []
        try:
            services = [s for s in bus.list_names() if str(s).startswith("org.mpris.MediaPlayer2.")]
            for s in services:
                try:
                    obj = bus.get_object(s, "/org/mpris/MediaPlayer2")
                    props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")
                    status = str(props.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus"))
                    if status == "Playing":
                        player = dbus.Interface(obj, "org.mpris.MediaPlayer2.Player")
                        player.Pause()
                        self._paused_by_kduck.add(str(s))
                        paused.append(str(s))
                except Exception:
                    continue
        except Exception:
            pass

        return paused

    def resume_players(self) -> List[str]:
        """Reanuda únicamente los reproductores que fueron pausados por KDuck."""
        bus = self._get_bus()
        if not bus or not self._paused_by_kduck:
            return []

        resumed = []
        for s in list(self._paused_by_kduck):
            try:
                obj = bus.get_object(s, "/org/mpris/MediaPlayer2")
                player = dbus.Interface(obj, "org.mpris.MediaPlayer2.Player")
                player.Play()
                resumed.append(s)
            except Exception:
                continue

        self._paused_by_kduck.clear()
        return resumed
