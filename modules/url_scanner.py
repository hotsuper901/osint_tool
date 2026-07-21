import json
import hashlib
from urllib.parse import urlparse
from utils import http_get, is_valid_url, save_result

def analyze_url_structure(url):
    lines = []
    try:
        parsed = urlparse(url)
        lines.append(f"  Scheme      : {parsed.scheme}")
        lines.append(f"  Hostname    : {parsed.hostname}")
        lines.append(f"  Port        : {parsed.port or 'default'}")
        lines.append(f"  Path        : {parsed.path or '/'}")
        lines.append(f"  Params      : {parsed.params or 'none'}")
        lines.append(f"  Query       : {parsed.query or 'none'}")
        lines.append(f"  Fragment    : {parsed.fragment or 'none'}")

        # Check for IP in URL
        import socket
        try:
            socket.inet_aton(parsed.hostname)
            lines.append(f"  [!] URL uses IP instead of domain")
        except:
            pass

        # Check for suspicious keywords
        suspicious = ['login', 'verify', 'update', 'confirm', 'secure',
                     'account', 'signin', 'bank', 'paypal', 'password']
        url_lower = url.lower()
        found_suspicious = [k for k in suspicious if k in url_lower]
        if found_suspicious:
            lines.append(f"  [!] Suspicious keywords: {', '.join(found_suspicious)}")

        # Check URL length
        if len(url) > 100:
            lines.append(f"  [!] Long URL ({len(url)} chars) - possible phishing")

        # Check @ symbol
        if '@' in url:
            lines.append("  [!] Contains @ - credential harvesting attempt")

        # Check multiple subdomains
        parts = parsed.hostname.split('.') if parsed.hostname else []
        if len(parts) > 3:
            lines.append(f"  [!] Many subdomain levels: {'.'.join(parts)}")
    except:
        lines.append("  [-] URL parsing failed")
    return lines

def check_virustotal(url):
    lines = []
    try:
        url_id = hashlib.sha256(url.encode()).hexdigest()
        r = http_get(f"https://www.virustotal.com/api/v3/urls/{url_id}")
        if r.status_code == 200:
            data = r.json()
            stats = data.get('data',{}).get('attributes',{}).get('last_analysis_stats',{})
            if stats:
                lines.append(f"  VT Malicious: {stats.get('malicious',0)}")
                lines.append(f"  VT Suspicious: {stats.get('suspicious',0)}")
                lines.append(f"  VT Harmless : {stats.get('harmless',0)}")
            else:
                lines.append("  VT: Not yet analyzed")
        elif r.status_code == 401:
            lines.append("  VT: API key required (free tier)")
        else:
            lines.append(f"  VT: {r.status_code}")
    except:
        lines.append("  VT: Unavailable")
    return lines

def check_urlscan(url):
    lines = []
    try:
        r = http_get(f"https://urlscan.io/api/v1/search/?q={url}")
        if r.status_code == 200:
            data = r.json()
            total = data.get('total', 0)
            lines.append(f"  urlscan.io : {total} results")
            for res in data.get('results', [])[:3]:
                page = res.get('page', {})
                lines.append(f"    IP: {page.get('ip','?')} Server: {page.get('server','?')} Country: {page.get('country','?')}")
        else:
            lines.append(f"  urlscan.io : {r.status_code}")
    except:
        lines.append("  urlscan.io: Unavailable")
    return lines

def check_phish_tank(url):
    lines = []
    try:
        r = http_get(f"https://checkurl.phishtank.com/checkurl/index.php?url={url}&format=json")
        if r.status_code == 200:
            data = r.json()
            if data.get('in_database'):
                lines.append(f"  [!] Listed in PhishTank as: {data.get('phish_detail_page','?')}")
            else:
                lines.append("  [+] Not in PhishTank database")
    except:
        pass
    return lines

def check_shortener(url):
    lines = []
    shorteners = {
        'bit.ly': 'Bitly', 'tinyurl.com': 'TinyURL', 'goo.gl': 'Google',
        't.co': 'Twitter', 'ow.ly': 'OWLY', 'buff.ly': 'Buffer',
        'is.gd': 'IsGD', 'cli.gs': 'CliGs', 'rebrand.ly': 'Rebrandly',
        'cutt.ly': 'Cuttly', 'shorte.st': 'Shorte', 'adf.ly': 'AdFly',
    }
    parsed = urlparse(url)
    domain = parsed.hostname or ''
    for short_domain, name in shorteners.items():
        if short_domain in domain:
            lines.append(f"  [!] URL shortened by {name} ({short_domain})")
    return lines

def check_ssl_tls(url):
    lines = []
    if url.startswith('https'):
        lines.append("  [+] HTTPS enabled (SSL/TLS)")
    else:
        lines.append("  [!] No HTTPS - traffic not encrypted")
    return lines

def run(url):
    print(f"\n{'='*60}")
    print(f"  URL / LINK SCANNER - Target: {url}")
    print(f"{'='*60}")

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    output = [f"URL: {url}"]

    print("\n  [URL Structure Analysis]")
    s = analyze_url_structure(url)
    for l in s:
        print(l); output.append(l)

    print("\n  [VirusTotal Check]")
    v = check_virustotal(url)
    for l in v:
        print(l); output.append(l)

    print("\n  [urlscan.io]")
    u = check_urlscan(url)
    for l in u:
        print(l); output.append(l)

    print("\n  [PhishTank]")
    p = check_phish_tank(url)
    for l in p:
        print(l); output.append(l)

    print("\n  [URL Shortener Detection]")
    sh = check_shortener(url)
    for l in sh:
        print(l); output.append(l)

    print("\n  [SSL/TLS]")
    t = check_ssl_tls(url)
    for l in t:
        print(l); output.append(l)

    # Try fetching the page
    print("\n  [HTTP Response]")
    try:
        r = http_get(url)
        print(f"    Status : {r.status_code}")
        print(f"    Size   : {len(r.content)} bytes")
        print(f"    Type   : {r.headers.get('Content-Type','?')}")
        print(f"    Server : {r.headers.get('Server','?')}")
        output.append(f"Status: {r.status_code}")
        output.append(f"Size: {len(r.content)} bytes")
        output.append(f"Type: {r.headers.get('Content-Type','?')}")
        output.append(f"Server: {r.headers.get('Server','?')}")

        # Check redirects
        if len(r.history) > 0:
            print(f"    Redirects: {len(r.history)}")
            for i, resp in enumerate(r.history):
                print(f"      [{i+1}] {resp.url} -> {resp.status_code}")
                output.append(f"  Redirect [{i+1}]: {resp.url} -> {resp.status_code}")
        output.append(f"Final URL: {r.url}")

    except Exception as e:
        print(f"    [-] Error: {e}")
        output.append(f"Error: {e}")

    save_result("url", url, "\n".join(output))
