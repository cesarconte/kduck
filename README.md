# KDuck 🦆

**Intelligent Auto-Ducking for PipeWire & WirePlumber 0.5 on KDE Plasma 6 / Wayland.**

KDuck monitoriza llamadas entrantes (KDE Connect Telephony), streams de comunicación por voz (Discord, Telegram, Teams, Zoom, WebRTC) y voz activa para atenuar de forma suave y logarítmica la música multimedia (Spotify, navegadores, VLC, etc.) y restaurarla fluidamente al finalizar.

---

## ✨ Características

- 📉 **Rampa Suave Logarítmica:** Atenuación de volumen progresiva en 350ms (sin cortes bruscos) y recuperación gradual en 500ms mediante `wpctl`.
- ⏯️ **MPRIS Pause/Resume Opcional:** Capaz de pausar reproductores locales si se prefiere no solo bajar el volumen.
- 📱 **Integración Nativa con KDE Connect:** Detecta llamadas entrantes (`Ringing` / `Talking`) y silencia o reduce el audio al instante.
- 🎙️ **Monitor PipeWire / WirePlumber 0.5:** Detección de streams de comunicación (`media.role=Communication`, `Voice`, `Phone`) mediante eventos en tiempo real sin polling continuo.
- ⚙️ **Configuración TOML Sencilla:** Ajustes en `~/.config/kduck/config.toml`.
- ⚡ **Servicio Systemd de Usuario:** Ligero, seguro y con consumo de CPU virtualmente nulo (0%).

---

## 🚀 Instalación Rápida

### Vía instalador autónomo:
```bash
git clone https://github.com/cesarconte/kduck.git
cd kduck
chmod +x install.sh
./install.sh
```

### En Arch Linux / CachyOS (vía PKGBUILD):
```bash
makepkg -si
```

---

## 🛠️ Uso y Comandos CLI

```bash
# Ver estado del audio y del servicio
kduck status

# Probar atenuación manual al 15%
kduck duck 15

# Restaurar volumen original
kduck unduck

# Editar configuración
kduck edit
```

---

## 📄 Licencia

GPL-3.0-or-later © 2026 Cesar <yugurta@gmail.com>
