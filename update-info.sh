#!/bin/sh
# ponytail: posix sh generator for static server telemetry, upgrade to systemd service if real-time metrics needed
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
TARGET="${1:-info.json}"

OS=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"')
[ -z "$OS" ] && OS=$(uname -s)

KERNEL=$(uname -sr)
HOST=$(hostname)
UPTIME=$(uptime -p 2>/dev/null || uptime | awk -F'( |,|:)+' '{print $6,"hrs,", $7,"min"}')
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
[ -z "$IP" ] && IP="127.0.0.1"

GATEWAY=$(ip route 2>/dev/null | awk '/default/ {print $3; exit}')
[ -z "$GATEWAY" ] && GATEWAY="N/A"

if command -v nginx >/dev/null 2>&1; then
  SERVER=$(nginx -v 2>&1 | sed 's/nginx version: //')
elif command -v apache2 >/dev/null 2>&1; then
  SERVER=$(apache2 -v 2>&1 | head -n1 | awk '{print $3}')
elif command -v httpd >/dev/null 2>&1; then
  SERVER=$(httpd -v 2>&1 | head -n1 | awk '{print $3}')
elif command -v caddy >/dev/null 2>&1; then
  SERVER=$(caddy version | awk '{print "Caddy", $1}')
else
  SERVER="Tidak ditemukan (jalankan: apt install nginx)"
fi

cat <<EOF > "$TARGET"
{
  "os": "$OS",
  "kernel": "$KERNEL",
  "hostname": "$HOST",
  "uptime": "$UPTIME",
  "server_ip": "$IP",
  "gateway": "$GATEWAY",
  "web_server": "$SERVER",
  "updated_at": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF
