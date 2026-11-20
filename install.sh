#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# install.sh: Instalador autónomo de KDuck para PipeWire & WirePlumber 0.5 sobre KDE Plasma 6 (instalación estricta en /usr)

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="/usr/bin/kduck"
SHARE_DIR="/usr/share/kduck"
APPS_PATH="/usr/share/applications/org.cesar.kduck.desktop"
SYSTEMD_PATH="/usr/lib/systemd/user/kduck.service"

echo "==> Instalando KDuck (Auto-Ducking Inteligente para PipeWire & WirePlumber) estrictamente en /usr..."

# 1. Comprobar dependencias
MISSING_DEPS=()
for dep in python3 wpctl pw-dump; do
    if ! command -v "$dep" >/dev/null 2>&1; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "⚠️  Faltan dependencias: ${MISSING_DEPS[*]}"
    if command -v pacman >/dev/null 2>&1; then
        echo "--> Instálalas con: sudo pacman -S --needed python wireplumber pipewire"
    fi
fi

# 2. Instalar módulos del motor en /usr/share/kduck/src
sudo -n mkdir -p "${SHARE_DIR}/src"
sudo -n cp -r "${SCRIPT_DIR}/src/"* "${SHARE_DIR}/src/"
echo "  ✓ Módulos de ducking y monitor PipeWire instalados en ${SHARE_DIR}"

# 3. Instalar ejecutable CLI en /usr/bin
sudo -n install -m 755 "${SCRIPT_DIR}/bin/kduck" "$BIN_PATH"
echo "  ✓ Binario instalado en $BIN_PATH"

# 4. Inicializar configuración predeterminada si no existe
"$BIN_PATH" status >/dev/null 2>&1 || true
echo "  ✓ Configuración inicializada en ~/.config/kduck/config.toml"

# 5. Instalar lanzador de escritorio
sudo -n install -m 644 "${SCRIPT_DIR}/data/org.cesar.kduck.desktop" "$APPS_PATH"
echo "  ✓ Lanzador registrado en $APPS_PATH"

# 6. Instalar y habilitar servicio systemd de usuario
sudo -n install -Dm644 "${SCRIPT_DIR}/data/kduck.service" "$SYSTEMD_PATH"
if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload
    systemctl --user enable --now kduck.service 2>/dev/null || true
    echo "  ✓ Servicio systemd de usuario 'kduck.service' habilitado y activo"
fi

# 7. Actualizar base de datos de aplicaciones
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
    echo "  ✓ Base de datos Sycoca de KDE actualizada"
fi

echo ""
echo "🎉 ¡Instalación de KDuck completada con éxito en /usr!"
echo "   - Servicio en segundo plano monitorizando llamadas y eventos de voz."
echo "   - Estado: ejecuta 'kduck status'"
echo "   - Configuración: ejecuta 'kduck edit' (~/.config/kduck/config.toml)"
