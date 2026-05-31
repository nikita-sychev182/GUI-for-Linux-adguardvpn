#!/usr/bin/env python3
import sys
import subprocess
import re
from PyQt5 import QtWidgets, QtGui, QtCore


def run_cmd(cmd_args, timeout=30):
    try:
        proc = subprocess.run(cmd_args, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, timeout=timeout)
        if proc.returncode == 0:
            return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
        stderr_lower = proc.stderr.strip().lower()
        is_privileged = (
            len(cmd_args) > 1 and cmd_args[1] in ('connect', 'disconnect')
        )
        if is_privileged and 'sudo' not in [a.lower() for a in cmd_args]:
            sudo_cmd = ['sudo', '-E'] + cmd_args
            proc2 = subprocess.run(sudo_cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, timeout=timeout)
            if proc2.returncode == 0:
                return proc2.returncode, proc2.stdout.strip(), proc2.stderr.strip()
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


class AdGuardWrapper:
    def __init__(self):
        self.cmd = 'adguardvpn-cli'

    def call(self, args):
        cli = [self.cmd] + args
        return run_cmd(cli)

    def login(self):
        return self.call(['login'])

    def logout(self):
        return self.call(['logout'])

    def list_locations(self):
        return self.call(['list-locations'])

    def connect(self, iso):
        return self.call(['connect', '-l', iso])

    def disconnect(self):
        return self.call(['disconnect'])

    def status(self):
        return self.call(['status'])

    def license(self):
        return self.call(['license'])

    def check_update(self):
        return self.call(['check-update'])

    def update(self):
        return self.call(['update'])

    def export_logs(self):
        return self.call(['export-logs'])

    def config(self):
        return self.call(['config'])


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AdGuard VPN GUI')
        self.resize(800, 500)

        self.wrapper = AdGuardWrapper()

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Top controls
        top_row = QtWidgets.QHBoxLayout()
        self.login_btn = QtWidgets.QPushButton('Login')
        self.logout_btn = QtWidgets.QPushButton('Logout')
        self.status_btn = QtWidgets.QPushButton('Status')
        top_row.addWidget(self.login_btn)
        top_row.addWidget(self.logout_btn)
        top_row.addWidget(self.status_btn)
        top_row.addStretch()

        layout.addLayout(top_row)

        # Search and list
        search_layout = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText('Search country or city...')
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        body = QtWidgets.QHBoxLayout()

        self.list_widget = QtWidgets.QListWidget()
        body.addWidget(self.list_widget, 3)

        right_col = QtWidgets.QVBoxLayout()
        self.connect_btn = QtWidgets.QPushButton('Connect')
        self.disconnect_btn = QtWidgets.QPushButton('Disconnect')
        self.status_label = QtWidgets.QLabel('Status: Unknown')
        self.output_box = QtWidgets.QTextEdit()
        self.output_box.setReadOnly(True)

        right_col.addWidget(self.connect_btn)
        right_col.addWidget(self.disconnect_btn)
        right_col.addWidget(self.status_label)
        right_col.addWidget(self.output_box, 1)

        body.addLayout(right_col, 5)

        layout.addLayout(body)

        # Bottom actions
        bottom = QtWidgets.QHBoxLayout()
        self.license_btn = QtWidgets.QPushButton('License')
        self.check_update_btn = QtWidgets.QPushButton('Check Update')
        self.update_btn = QtWidgets.QPushButton('Update')
        self.export_logs_btn = QtWidgets.QPushButton('Export Logs')
        bottom.addWidget(self.license_btn)
        bottom.addWidget(self.check_update_btn)
        bottom.addWidget(self.update_btn)
        bottom.addWidget(self.export_logs_btn)
        bottom.addStretch()
        layout.addLayout(bottom)

        # Signals
        self.login_btn.clicked.connect(self.handle_login)
        self.logout_btn.clicked.connect(self.handle_logout)
        self.status_btn.clicked.connect(self.handle_status)
        self.connect_btn.clicked.connect(self.handle_connect)
        self.disconnect_btn.clicked.connect(self.handle_disconnect)
        self.license_btn.clicked.connect(self.handle_license)
        self.check_update_btn.clicked.connect(self.handle_check_update)
        self.update_btn.clicked.connect(self.handle_update)
        self.export_logs_btn.clicked.connect(self.handle_export_logs)
        self.search_edit.textChanged.connect(self.filter_locations)

        # initial load
        self.locations = []
        self.load_locations()

    def append_output(self, title, out, err):
        text = f"--- {title} ---\n"
        if out:
            text += out + "\n"
        if err:
            text += "ERR: " + err + "\n"
        self.output_box.append(text)

    def safe_call(self, fn, *args):
        code, out, err = fn(*args)
        return code, out, err

    def handle_login(self):
        code, out, err = self.safe_call(self.wrapper.login)
        self.append_output('login', out, err)

    def handle_logout(self):
        code, out, err = self.safe_call(self.wrapper.logout)
        self.append_output('logout', out, err)

    def handle_status(self):
        code, out, err = self.safe_call(self.wrapper.status)
        if out:
            self.status_label.setText('Status: ' + out.splitlines()[0])
        self.append_output('status', out, err)

    def handle_connect(self):
        item = self.list_widget.currentItem()
        if not item:
            QtWidgets.QMessageBox.warning(self, 'Select', 'Please select a location to connect')
            return
        iso = item.data(QtCore.Qt.UserRole)
        code, out, err = self.safe_call(self.wrapper.connect, iso)
        self.append_output(f'connect {iso}', out, err)

    def handle_disconnect(self):
        code, out, err = self.safe_call(self.wrapper.disconnect)
        self.append_output('disconnect', out, err)

    def handle_license(self):
        code, out, err = self.safe_call(self.wrapper.license)
        self.append_output('license', out, err)

    def handle_check_update(self):
        code, out, err = self.safe_call(self.wrapper.check_update)
        self.append_output('check-update', out, err)

    def handle_update(self):
        code, out, err = self.safe_call(self.wrapper.update)
        self.append_output('update', out, err)

    def handle_export_logs(self):
        code, out, err = self.safe_call(self.wrapper.export_logs)
        self.append_output('export-logs', out, err)

    def load_locations(self):
        code, out, err = self.safe_call(self.wrapper.list_locations)
        loc_text = out or ''
        if not loc_text:
            loc_text = self._fallback_locations_text()
        self.locations = self._parse_locations(loc_text)
        self.populate_list()

    def populate_list(self):
        self.list_widget.clear()
        for loc in self.locations:
            display = f"{loc['ISO']} - {loc['COUNTRY']} / {loc['CITY']} (ping {loc.get('PING','')})"
            item = QtWidgets.QListWidgetItem(display)
            item.setData(QtCore.Qt.UserRole, loc['ISO'])
            self.list_widget.addItem(item)

    def filter_locations(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _parse_locations(self, text):
        ansi_re = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        raw_lines = [ansi_re.sub('', l).strip() for l in text.splitlines() if l.strip()]
        results = []
        for l in raw_lines:
            # skip header lines that include column names
            up = l.upper()
            if 'ISO' in up and 'COUNTRY' in up:
                continue
            # expect lines beginning with 2-letter ISO code
            m = re.match(r'^([A-Z]{2})\b(.*)$', l)
            if not m:
                continue
            iso = m.group(1)
            rest = m.group(2).strip()
            # split by 2+ spaces to detect columns (ISO  COUNTRY   CITY   PING)
            cols = [c.strip() for c in re.split(r'\s{2,}', l) if c.strip()]
            country = ''
            city = ''
            ping = ''
            if len(cols) == 1:
                # format: "LV Latvia" (fallback)
                parts = cols[0].split(None, 1)
                if len(parts) >= 2:
                    country = parts[1]
            else:
                # first column contains ISO + country
                first = cols[0].split(None, 1)
                if len(first) >= 2:
                    country = first[1]
                # second column is usually city
                if len(cols) >= 2:
                    city = cols[1]
                # last column might contain ping number
                last = cols[-1]
                last_num = re.findall(r"(\d+)", last)
                if last_num:
                    ping = last_num[-1]
            results.append({'ISO': iso, 'COUNTRY': country, 'CITY': city, 'PING': ping})
        return results

    def _fallback_locations_text(self):
        # Try to get live list from adguardvpn-cli and extract ISO + COUNTRY
        try:
            code, out, err = self.wrapper.list_locations()
            if out:
                ansi_re = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
                lines = [ansi_re.sub('', l).strip() for l in out.splitlines() if l.strip()]
                result_lines = []
                for l in lines:
                    up = l.upper()
                    if 'ISO' in up and 'COUNTRY' in up:
                        continue
                    # try match ISO at line start
                    m = re.match(r'^([A-Z]{2})\b(.*)$', l)
                    if not m:
                        # fallback: split by 2+ spaces
                        parts = [c.strip() for c in re.split(r'\s{2,}', l) if c.strip()]
                        if parts:
                            first = parts[0].split(None, 1)
                            if len(first) >= 2:
                                iso = first[0]
                                country = first[1]
                                result_lines.append(f"{iso} {country}")
                        continue
                    iso = m.group(1)
                    # split into columns by 2+ spaces
                    cols = [c.strip() for c in re.split(r'\s{2,}', l) if c.strip()]
                    country = ''
                    if cols:
                        first = cols[0].split(None, 1)
                        if len(first) >= 2:
                            country = first[1]
                        else:
                            country = m.group(2).strip()
                    else:
                        country = m.group(2).strip()
                    result_lines.append(f"{iso} {country}")
                if result_lines:
                    return '\n'.join(result_lines)
        except Exception:
            pass

        # Static fallback if CLI not available or parsing failed
        return '''
LV Latvia
CH Switzerland
DK Denmark
DE Germany
FR France
AT Austria
GB United Kingdom
NL Netherlands
EE Estonia
CZ Czechia
UA Ukraine
BE Belgium
IT Italy
SK Slovakia
LU Luxembourg
HR Croatia
IE Ireland
BG Bulgaria
ES Spain
NO Norway
PL Poland
FI Finland
HU Hungary
EG Egypt
LT Lithuania
RS Serbia
PT Portugal
RO Romania
SE Sweden
MD Moldova
GR Greece
TR Turkey
IS Iceland
IL Israel
IR Iran
CY Cyprus
US United States
CA Canada
RU Russia
AE UAE
NG Nigeria
KH Cambodia
SG Singapore
NP Nepal
ZA South Africa
ID Indonesia
VN Vietnam
IN India
PH Philippines
TW Taiwan
PE Peru
MX Mexico
CO Colombia
TH Thailand
KZ Kazakhstan
CN China
BR Brazil
CL Chile
AR Argentina
HK Hong Kong
JP Japan
KR South Korea
NZ New Zealand
AU Australia
'''

    def closeEvent(self, event):
        # Do not disconnect AdGuard VPN on GUI close — leave service running in background
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
