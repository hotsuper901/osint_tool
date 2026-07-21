import os
import json
import datetime
from urllib.parse import urlparse

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

def ensure_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)

def save_result(module, target, data):
    ensure_results_dir()
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in target)[:30]
    filename = f"{module}_{safe_name}_{ts}.txt"
    filepath = os.path.join(RESULTS_DIR, filename)

    with open(filepath, "w") as f:
        f.write(f"OSINT MAX Toolkit - Result\n")
        f.write(f"Module: {module}\n")
        f.write(f"Target: {target}\n")
        f.write(f"Date:   {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(data)

    print(f"\n[💾] Result saved: {filepath}")
    return filepath

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_valid_ip(ip):
    import socket
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

def is_valid_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def http_get(url, headers=None, timeout=10, verify=False):
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/json,*/*",
    }
    if headers:
        default_headers.update(headers)
    return requests.get(url, headers=default_headers, timeout=timeout, verify=verify)
