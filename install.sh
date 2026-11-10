#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Cesar <yugurta@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# install.sh: Instalador autónomo de KDuck para PipeWire & WirePlumber 0.5 sobre KDE Plasma 6

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
SHARE_DIR="${HOME}/.local/share/kduck"
APPS_DIR="${HOME}/.local/share/applications"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

echo "==> Instalando KDuck (Auto-Ducking Inteligente para PipeWire & WirePlumber)..."

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

# 2. Instalar módulos del motor
mkdir -p "${SHARE_DIR}/src"
cp -r "${SCRIPT_DIR}/src/"* "${SHARE_DIR}/src/"
echo "  ✓ Módulos de ducking y monitor PipeWire instalados en ${SHARE_DIR}"

# 3. Instalar ejecutable CLI
mkdir -p "$BIN_DIR"
install -m 755 "${SCRIPT_DIR}/bin/kduck" "${BIN_DIR}/kduck"
echo "  ✓ Binario instalado en ${BIN_DIR}/kduck"

# 4. Inicializar configuración predeterminada si no existe
"${BIN_DIR}/kduck" status >/dev/null 2>&1 || true
echo "  ✓ Configuración inicializada en ~/.config/kduck/config.toml"

# 5. Instalar lanzador de escritorio
mkdir -p "$APPS_DIR"
install -m 644 "${SCRIPT_DIR}/data/org.cesar.kduck.desktop" "${APPS_DIR}/org.cesar.kduck.desktop"
echo "  ✓ Lanzador registrado en ${APPS_DIR}/org.cesar.kduck.desktop"

# 6. Instalar y habilitar servicio systemd de usuario
mkdir -p "$SYSTEMD_DIR"
install -m 644 "${SCRIPT_DIR}/data/kduck.service" "${SYSTEMD_DIR}/kduck.service"
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
echo "🎉 ¡Instalación de KDuck completada con éxito!"
echo "   - Servicio en segundo plano monitorizando llamadas y eventos de voz."
echo "   - Estado: ejecuta 'kduck status'"
echo "   - Configuración: ejecuta 'kduck edit' (~/.config/kduck/config.toml)"
