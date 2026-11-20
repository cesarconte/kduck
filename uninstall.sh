#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# uninstall.sh: Desinstalador de KDuck

set -eo pipefail

echo "==> Desinstalando KDuck de /usr..."

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user stop kduck.service 2>/dev/null || true
    systemctl --user disable kduck.service 2>/dev/null || true
    systemctl --user daemon-reload
fi

sudo -n rm -f "/usr/bin/kduck"
sudo -n rm -rf "/usr/share/kduck"
sudo -n rm -f "/usr/share/applications/org.cesar.kduck.desktop"
sudo -n rm -f "/usr/lib/systemd/user/kduck.service"

if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo "✓ Desinstalación de KDuck completada."
