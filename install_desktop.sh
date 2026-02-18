#!/usr/bin/env bash
# Install a .desktop launcher into the user's applications menu.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="$HOME/.local/share/applications"
mkdir -p "$DEST_DIR"

[ -d "$DEST_DIR" ] || mkdir -p "$DEST_DIR"
DESKTOP_FILE="$DEST_DIR/AdGuardVPN-GUI.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=AdGuard VPN GUI
Comment=Graphical wrapper for adguardvpn-cli
Exec=$DIR/run_adguardvpn_gui.sh
Icon=$DIR/icon.svg
Terminal=false
Type=Application
Categories=Network;Utility;
EOF

chmod +x "$DESKTOP_FILE"
echo "Installed launcher to $DESKTOP_FILE"
echo "If the icon doesn't appear, add a 64x64 PNG at $DIR/icon.png or edit the desktop file to point to an existing icon."
