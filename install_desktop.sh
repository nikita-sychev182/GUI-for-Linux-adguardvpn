#!/usr/bin/env bash
# Install a .desktop launcher into the user's applications menu.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="$HOME/.local/share/applications"
mkdir -p "$DEST_DIR"

[ -d "$DEST_DIR" ] || mkdir -p "$DEST_DIR"
DESKTOP_FILE="$DEST_DIR/AdGuardVPN-GUI.desktop"
[ -d "$HOME/.local/share/icons" ] || mkdir -p "$HOME/.local/share/icons"
ICON_DIR="$HOME/.local/share/icons"

# install icons into $ICON_DIR using a consistent base name
if [ -f "$DIR/icon.svg" ]; then
	cp "$DIR/icon.svg" "$ICON_DIR/adguardvpn-gui-icon.svg"
fi
if [ -f "$DIR/icon.png" ]; then
	cp "$DIR/icon.png" "$ICON_DIR/adguardvpn-gui-icon.png"
fi

# prefer SVG if available, fallback to PNG
if [ -f "$ICON_DIR/adguardvpn-gui-icon.svg" ]; then
	ICON_PATH="$ICON_DIR/adguardvpn-gui-icon.svg"
elif [ -f "$ICON_DIR/adguardvpn-gui-icon.png" ]; then
	ICON_PATH="$ICON_DIR/adguardvpn-gui-icon.png"
else
	ICON_PATH="$DIR/icon.svg"
fi

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=AdGuard VPN GUI
Comment=Graphical wrapper for adguardvpn-cli
Exec=$DIR/run_adguardvpn_gui.sh
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Network;Utility;
EOF

chmod +x "$DESKTOP_FILE"
echo "Installed launcher to $DESKTOP_FILE"
echo "Installed icons (if found) to $ICON_DIR/adguardvpn-gui-icon.{svg,png}"
echo "If the icon doesn't appear, add a 64x64 PNG at $DIR/icon.png or edit the desktop file to point to an existing icon."
