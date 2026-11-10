#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# uninstall.sh: Desinstalador autónomo de KDuck

set -eo pipefail

BIN_DIR="${HOME}/.local/bin"
SHARE_DIR="${HOME}/.local/share/kduck"
APPS_DIR="${HOME}/.local/share/applications"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

echo "==> Desinstalando KDuck..."

# Detener y deshabilitar servicio systemd
if command -v systemctl >/dev/null 2>&1; then
    systemctl --user stop kduck.service 2>/dev/null || true
    systemctl --user disable kduck.service 2>/dev/null || true
fi
rm -f "${SYSTEMD_DIR}/kduck.service"
systemctl --user daemon-reload 2>/dev/null || true
echo "  ✓ Servicio systemd detenido y eliminado"

# Eliminar binario y módulos
rm -f "${BIN_DIR}/kduck"
rm -rf "$SHARE_DIR"
echo "  ✓ Binario y módulos eliminados"

# Eliminar lanzador
rm -f "${APPS_DIR}/org.cesar.kduck.desktop"
echo "  ✓ Lanzador de aplicaciones eliminado"

if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo "🎉 ¡KDuck ha sido desinstalado correctamente!"
echo "   Nota: Los archivos de configuración en ~/.config/kduck se han conservado por seguridad."
