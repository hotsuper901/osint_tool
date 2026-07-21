import socket
import ssl
import json
import datetime
from utils import http_get, save_result

def dns_records(domain):
    lines = []
    try:
        ip = socket.gethostbyname(domain)
        lines.append(f"  A Record    : {ip}")
        try:
            ips = socket.getaddrinfo(domain, None)
            seen = set()
            for i in ips:
                addr = i[4][0]
                if addr not in seen and addr != ip:
                    seen.add(addr)
                    lines.append(f"  Alt IP      : {addr}")
        except:
            pass
    except:
        lines.append("  A Record    : FAILED")
        return lines

    import dns.resolver
    for qtype in ['AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']:
        try:
            answers = dns.resolver.resolve(domain, qtype)
            for rdata in answers[:5]:
                text = str(rdata).replace('"', '')
                lines.append(f"  {qtype:<11s}: {text}")
                if qtype == 'MX':
                    mx_parts = text.split()
                    if len(mx_parts) >= 2:
                        try:
                            mx_ip = socket.gethostbyname(mx_parts[1])
                            lines.append(f"              -> {mx_ip}")
                        except:
                            pass
        except:
            pass
    return lines

def whois_lookup(domain):
    lines = []
    try:
        r = http_get(f"https://who-dat.as93.net/{domain}")
        if r.status_code == 200:
            d = r.json()
            if 'registrar' in d:
                lines.append(f"  Registrar   : {d['registrar']}")
            if 'created' in d:
                lines.append(f"  Created     : {d['created']}")
            if 'expires' in d:
                lines.append(f"  Expires     : {d['expires']}")
            if 'updated' in d:
                lines.append(f"  Updated     : {d['updated']}")
            if 'nameservers' in d:
                ns = d['nameservers']
                lines.append(f"  Name Svr    : {', '.join(ns[:5])}")
            if 'registrant_name' in d:
                lines.append(f"  Registrant  : {d['registrant_name']}")
            if 'registrant_organization' in d:
                lines.append(f"  Org         : {d['registrant_organization']}")
            if 'admin_email' in d:
                lines.append(f"  Admin Email : {d['admin_email']}")
            if 'tech_email' in d:
                lines.append(f"  Tech Email  : {d['tech_email']}")
        else:
            lines.append(f"  WHOIS status: {r.status_code}")
    except:
        lines.append("  WHOIS: Unavailable")
    return lines

def ssl_cert(domain):
    lines = []
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(5)
            s.connect((domain, 443))
            cert = s.getpeercert()
            if cert:
                subj = dict(x[0] for x in cert.get('subject', []))
                issuer = dict(x[0] for x in cert.get('issuer', []))
                lines.append(f"  Subject     : {subj.get('commonName','?')}")
                lines.append(f"  Issuer      : {issuer.get('commonName','?')}")
                lines.append(f"  Org         : {subj.get('organizationName','?')}")
                lines.append(f"  SAN         : {', '.join(cert.get('subjectAltName', []))}")
                lines.append(f"  NotBefore   : {cert.get('notBefore','?')}")
                lines.append(f"  NotAfter    : {cert.get('notAfter','?')}")
                lines.append(f"  Serial      : {cert.get('serialNumber','?')}")
                lines.append(f"  Version     : {cert.get('version','?')}")
    except:
        lines.append("  SSL: Failed or no HTTPS")
    return lines

def http_headers(domain):
    lines = []
    for proto in ['https', 'http']:
        try:
            r = http_get(f"{proto}://{domain}")
            lines.append(f"  [{proto.upper()} {r.status_code}]")
            interesting = ['Server','X-Powered-By','X-Framework','Via','X-Generator',
                          'CF-Ray','CF-Cache-Status','X-Amz-','X-Server-','X-Aspnet-']
            for k, v in r.headers.items():
                for pat in interesting:
                    if k.lower().startswith(pat.lower()):
                        lines.append(f"    {k}: {v}")
            break
        except:
            continue
    return lines

def subdomain_enum(domain):
    lines = []
    subs = [
        "www", "mail", "ftp", "admin", "api", "blog", "dev", "test",
        "stage", "cdn", "m", "mobile", "webmail", "smtp", "pop", "ns1",
        "ns2", "vpn", "remote", "support", "help", "forum", "shop",
        "app", "beta", "demo", "secure", "login", "portal", "dns",
        "mx", "server", "git", "docs", "wiki", "status", "staging"
    ]
    lines.append("  [Subdomain Discovery]")
    found = []
    for sub in subs:
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            found.append((sub, ip))
        except:
            pass
    if found:
        for sub, ip in found:
            lines.append(f"    {sub:<15s} -> {ip}")
    else:
        lines.append("    No subdomains found via basic enumeration")
    return lines

def wayback_urls(domain):
    lines = []
    try:
        r = http_get(f"https://web.archive.org/cdx/search/cdx?url=*.{domain}&output=json&limit=10&fl=original,timestamp")
        if r.status_code == 200:
            data = r.json()
            if len(data) > 1:
                lines.append(f"  Wayback: {len(data)-1} snapshots")
                for entry in data[1:6]:
                    url = entry[0] if len(entry) > 0 else ''
                    ts = entry[1] if len(entry) > 1 else ''
                    lines.append(f"    {ts}: {url}")
    except:
        pass
    return lines

def run(domain):
    print(f"\n{'='*60}")
    print(f"  DOMAIN INFORMATION - Target: {domain}")
    print(f"{'='*60}")

    output = []

    print("\n  [DNS Records]")
    d = dns_records(domain)
    for l in d:
        print(l); output.append(l)

    print("\n  [WHOIS]")
    w = whois_lookup(domain)
    for l in w:
        print(l); output.append(l)

    print("\n  [SSL Certificate]")
    s = ssl_cert(domain)
    for l in s:
        print(l); output.append(l)

    print("\n  [HTTP Headers]")
    h = http_headers(domain)
    for l in h:
        print(l); output.append(l)

    print("\n  [Subdomain Enumeration]")
    sb = subdomain_enum(domain)
    for l in sb:
        print(l); output.append(l)

    print("\n  [Wayback Machine]")
    wb = wayback_urls(domain)
    for l in wb:
        print(l); output.append(l)

    save_result("domain", domain, "\n".join(output))
