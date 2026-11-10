# Maintainer: Cesar <yugurta@gmail.com>
pkgname=kduck-git
pkgver=1.0.0
pkgrel=1
pkgdesc="Intelligent Auto-Ducking for PipeWire & WirePlumber 0.5 upon incoming calls, voice chat, and TTS on KDE Plasma"
arch=('any')
url="https://github.com/cesarconte/kduck"
license=('GPL-3.0-or-later')
depends=('python' 'pipewire' 'wireplumber')
optdepends=(
    'kdeconnect: para atenuación automática ante llamadas entrantes en el teléfono'
    'libnotify: para notificaciones de escritorio'
)
provides=('kduck')
conflicts=('kduck')
source=("git+https://github.com/cesarconte/kduck.git")
sha256sums=('SKIP')

pkgver() {
    cd "${srcdir}/kduck"
    printf "1.0.0.r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
    cd "${srcdir}/kduck"
    
    install -Dm755 bin/kduck "${pkgdir}/usr/bin/kduck"
    
    install -d "${pkgdir}/usr/share/kduck/src"
    cp -r src/* "${pkgdir}/usr/share/kduck/src/"
    
    install -Dm644 data/kduck.service "${pkgdir}/usr/lib/systemd/user/kduck.service"
    install -Dm644 data/org.cesar.kduck.desktop "${pkgdir}/usr/share/applications/org.cesar.kduck.desktop"
    install -Dm644 README.md "${pkgdir}/usr/share/doc/kduck/README.md"
}
