#!/usr/bin/env bash
# Ranger Pi recon — run ON the Pi to inventory the existing setup before we
# build anything. Read-only: it inspects and prints, changes nothing.
#
# Usage (from your Mac once the Pi is online):
#   ssh <user>@ranger 'bash -s' < dashboard/scripts/recon.sh | tee dashboard/capture/recon-$(date +%Y%m%d).txt
# or copy it over and run:  bash recon.sh
set +e

line() { printf '\n\033[1m=== %s ===\033[0m\n' "$1"; }

line "HOST / OS"
hostname; uname -a
cat /etc/os-release 2>/dev/null | grep -E 'PRETTY_NAME|VERSION'
uptime

line "CAN INTERFACES (ip link)"
ip -details -statistics link show 2>/dev/null | grep -A6 -i can || echo "no can interface found in 'ip link'"
echo "-- current can0 bitrate/state --"
ip -details link show can0 2>/dev/null || echo "can0 not present"

line "CAN KERNEL MODULES / HAT (dmesg + lsmod)"
lsmod | grep -Ei 'can|mcp251|slcan' || echo "no can modules loaded"
dmesg 2>/dev/null | grep -Ei 'mcp251|can0|spi' | tail -20 || echo "(dmesg needs sudo?)"
sudo dmesg 2>/dev/null | grep -Ei 'mcp251|can0|spi' | tail -20

line "BOOT CONFIG (overlays = which CAN HAT)"
for f in /boot/firmware/config.txt /boot/config.txt; do
  [ -f "$f" ] && { echo "--- $f ---"; grep -Ei 'dtoverlay|dtparam=spi|mcp251|can' "$f"; }
done

line "ORIGINAL SOFTWARE — likely project dirs"
ls -la /home/*/ 2>/dev/null
echo "-- searching for candidate projects (py/node/can) --"
find /home /opt /srv /root -maxdepth 4 \
  \( -iname '*.py' -o -iname 'package.json' -o -iname '*.service' -o -iname '*can*' -o -iname 'requirements.txt' \) \
  2>/dev/null | grep -vE 'site-packages|node_modules|/\.cache/' | head -80

line "PYTHON CAN-RELATED PACKAGES"
python3 -c 'import can; print("python-can", can.__version__)' 2>/dev/null || echo "python-can not installed system-wide"
pip3 list 2>/dev/null | grep -Ei 'can|cantools|flask|fastapi|dash|kivy|pygame|paho' || echo "(no obvious dashboard libs in pip3 list)"

line "AUTOSTART — systemd services (non-vendor)"
systemctl list-units --type=service --state=running 2>/dev/null | grep -vE 'systemd-|dbus|ssh|networkd|resolved|user@|getty|udev|rsyslog|cron|avahi|wpa|bluetooth|polkit|timesync' | head -40
echo "-- enabled custom services --"
systemctl list-unit-files --state=enabled 2>/dev/null | grep -vE 'getty|systemd|ssh|network|avahi|bluetooth|cron|udev|timesync|rsync|hciuart|raspi|dphys|triggerhappy|wpa'
echo "-- any unit mentioning can/ranger/dash/gauge --"
grep -rilE 'can0|ranger|dash|gauge|candump|socketcan' /etc/systemd/system /lib/systemd/system 2>/dev/null

line "AUTOSTART — cron / rc.local / autostart"
crontab -l 2>/dev/null; sudo crontab -l 2>/dev/null
cat /etc/rc.local 2>/dev/null | grep -vE '^#|^$|^exit'
ls /etc/xdg/autostart/ ~/.config/autostart/ 2>/dev/null

line "LISTENING PORTS (already-served dashboard?)"
ss -tlnp 2>/dev/null | grep -vE '127.0.0.53|:22 ' || sudo ss -tlnp 2>/dev/null | grep -vE '127.0.0.53|:22 '

line "DISPLAY / KIOSK"
echo "DISPLAY=$DISPLAY"; ls ~/.config/lxsession 2>/dev/null
pgrep -a chromium 2>/dev/null; pgrep -a X 2>/dev/null

line "GIT REPOS on the Pi"
find /home /opt /srv -maxdepth 4 -name .git -type d 2>/dev/null | while read g; do d=$(dirname "$g"); echo "$d"; git -C "$d" remote -v 2>/dev/null | head -1; git -C "$d" log --oneline -1 2>/dev/null; done

line "DONE"
echo "Recon complete. Paste this output back."
