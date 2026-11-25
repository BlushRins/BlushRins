#!/usr/bin/env bash
set -euo pipefail
target=${1:?Pass a directory for the profile fonts}
target=$(mkdir -p -- "$target" && realpath -- "$target")
cd "$target"

curl --fail --location --silent --show-error --retry 3 --max-time 90 \
  https://archive.archlinux.org/packages/i/inter-font/inter-font-4.1-1-any.pkg.tar.zst -o inter.tar.zst
curl --fail --location --silent --show-error --retry 3 --max-time 90 \
  https://archive.archlinux.org/packages/n/noto-fonts/noto-fonts-1%3A2026.11.01-1-any.pkg.tar.zst -o noto.tar.zst

tar -xf inter.tar.zst usr/share/fonts/inter/Inter.ttc
tar -xf noto.tar.zst usr/share/fonts/noto/NotoSansMono-{Regular,Bold}.ttf
sha256sum --check <<'SUMS'
ea4e3d9970b9b6b566110a1b0e13635fe235280b83dd2443dcb3faca1e2456ef  usr/share/fonts/inter/Inter.ttc
65b5e2b2c4a1fba9ae8be1f026cb35b03dcb8886d9b2a4147054fde12f7e767d  usr/share/fonts/noto/NotoSansMono-Regular.ttf
a21ea0ba6ea49fda7b34ca39a504b487f1130885d36e1a4f9f4255b3ba6994bc  usr/share/fonts/noto/NotoSansMono-Bold.ttf
SUMS
