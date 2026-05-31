#!/usr/bin/env bash
set -euo pipefail

SUDOERS_DIR="/etc/sudoers.d"
SUDOERS_FILE="$SUDOERS_DIR/adguardvpn-cli-nopasswd"

CLI_PATH="$(command -v adguardvpn-cli || true)"

if [ -z "$CLI_PATH" ]; then
    echo "ERROR: adguardvpn-cli not found in PATH. Install it first."
    exit 1
fi

GROUP=""
for g in wheel sudo admin; do
    if id -nG "$USER" | grep -qw "$g"; then
        GROUP="$g"
        break
    fi
done

if [ -z "$GROUP" ]; then
    echo "ERROR: Could not detect sudo group (wheel/sudo/admin). Edit script manually."
    exit 1
fi

POLICY="${GROUP} ALL=(ALL) NOPASSWD: ${CLI_PATH} connect *, ${CLI_PATH} disconnect *"

printf '%s\n' "$POLICY" | sudo tee "$SUDOERS_FILE" > /dev/null

sudo chmod 0440 "$SUDOERS_FILE"

if sudo visudo -c -f "$SUDOERS_FILE"; then
    echo "OK: $SUDOERS_FILE created and validated"
else
    echo "ERROR: syntax invalid, removing broken file"
    sudo rm -f "$SUDOERS_FILE"
    exit 1
fi
