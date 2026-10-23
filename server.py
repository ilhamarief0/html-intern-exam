#!/usr/bin/env python3
# ponytail: stdlib http backend for live telemetry; upgrade to fastcgi/gunicorn if high RPS
import http.server
import json
import os
import platform
import subprocess

def get_telemetry():
    os_name = platform.freedesktop_os_release().get('PRETTY_NAME', platform.system()) if hasattr(platform, 'freedesktop_os_release') else platform.system()
    kernel = f"{platform.system()} {platform.release()}"
    uptime = "N/A"
    try:
        with open('/proc/uptime') as f:
            sec = int(float(f.readline().split()[0]))
            h, m = divmod(sec // 60, 60)
            d, h = divmod(h, 24)
            uptime = f"{d}d {h}h {m}m {sec % 60}s" if d else f"{h}h {m}m {sec % 60}s"
    except Exception:
        pass

    gw = subprocess.getoutput("ip route 2>/dev/null | awk '/default/ {print $3; exit}'") or "N/A"
    ip = subprocess.getoutput("hostname -I 2>/dev/null | awk '{print $1}'") or "127.0.0.1"

    return {
        "os": os_name,
        "kernel": kernel,
        "hostname": platform.node(),
        "uptime": uptime,
        "server_ip": ip,
        "gateway": gw,
        "web_server": "Nginx"
    }

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/info.json'):
            payload = json.dumps(get_telemetry()).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(payload)
        else:
            super().do_GET()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f"Backend telemetri aktif di 127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
