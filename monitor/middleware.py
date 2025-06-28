import time
import json
from pathlib import Path
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Log file path (outside the app directory)
LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "api_logs.json"

# Ignore UI and system routes to avoid logging unnecessary entries
UI_IGNORE_PREFIXES = [
    '/dashboard', '/logs', '/settings', '/favicon.ico',
    '/static', '/admin', '/login', '/logout', '/register','/ws/'
]

class APILoggingMiddleware(MiddlewareMixin):
    RATE_LIMIT = 10  # max requests
    TIME_WINDOW = 60  # seconds
    request_log = {}  # {ip: [timestamps]}

    def process_request(self, request):
        ip = self._get_client_ip(request)

        # ⛔ Skip logging for background AJAX fetches (e.g., dashboard auto-refresh)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if settings.DEBUG:
                # ✅ Local development: Don't log AJAX polling
                return
            # 🚀 Production: Comment above if you want to monitor AJAX too

        # ⛔ Skip ignored paths (UI navigation)
        if self._is_ignored_path(request.path):
            return

        # Detect if proxy API (e.g., /proxy/...), set actual port
        is_proxy = request.path.startswith('/proxy/')
        real_port = 8143 if is_proxy else request.get_port()

        timestamp = int(time.time())
        endpoint = request.path
        method = request.method
        token = request.headers.get("Authorization", "None")
        payload = request.body.decode('utf-8', errors='ignore') if request.body else ""

        # Capture query string (?name=Bhanu, etc.)
        query_string = request.META.get("QUERY_STRING", "")
        if query_string:
            payload += f"?{query_string}"

        entry = {
            "timestamp": timestamp,
            "ip": ip,
            "port": real_port,
            "endpoint": endpoint,
            "method": method,
            "token": token,
            "payload": payload
        }

        self._append_to_file(entry)
        self._append_to_db(entry)
        self._detect_rate_abuse(ip, timestamp)
        self._send_to_ws(entry) 

    def _is_ignored_path(self, path):
        return any(path.startswith(prefix) for prefix in UI_IGNORE_PREFIXES)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def _append_to_file(self, data):
        try:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            print("📂 File Logging Error:", e)

    def _append_to_db(self, data):
        try:
            from .models import APILog
            APILog.objects.create(
                ip_address=data["ip"],
                port=data["port"],
                endpoint=data["endpoint"],
                method=data["method"],
                token=data["token"],
                payload=data["payload"]
            )
        except Exception as e:
            print("💾 DB Logging Error:", e)

        

    def _detect_rate_abuse(self, ip, current_time):
        timestamps = self.request_log.get(ip, [])
        timestamps.append(current_time)
        # Keep only timestamps within TIME_WINDOW
        timestamps = [t for t in timestamps if current_time - t <= self.TIME_WINDOW]
        self.request_log[ip] = timestamps

        if len(timestamps) > self.RATE_LIMIT:
            print(f"🚨 ALERT: IP {ip} exceeded {self.RATE_LIMIT} requests in {self.TIME_WINDOW} seconds!")

    def _send_to_ws(self, data):
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "logs",
                {
                    "type": "send_log",
                    "data": data
                }
            )
        except Exception as e:
            print("🧩 WebSocket Send Error:", e)
