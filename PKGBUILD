pkgname=global-proxy
pkgver=1
pkgrel=1
pkgdesc='Global proxy'
url=https://github.com/Henry-ZHR/global-proxy
license=(Unlicense)
source=(global-proxy.py global-proxy.service global-proxy.nft tproxy-servers.nft)
sha512sums=(SKIP SKIP SKIP SKIP)
arch=(any)
backup=(etc/global-proxy/tproxy-servers.nft)
depends=(
  nftables
  python
  python-pyroute2
)
optdepends=(
  python-argcomplete
)

package() {
  install -Dm755 global-proxy.py "${pkgdir}/usr/bin/global-proxy"
  install -Dm644 global-proxy.service "${pkgdir}/usr/lib/systemd/system/global-proxy.service"
  install -Dm644 global-proxy.nft "${pkgdir}/usr/share/global-proxy/global-proxy.nft"
  install -Dm644 tproxy-servers.nft "${pkgdir}/etc/global-proxy/tproxy-servers.nft"
}
