import socket
import json
from utils import http_get, is_valid_ip, save_result

def geo_lookup(ip):
    lines = []
    try:
        r = http_get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,query,mobile,proxy,hosting")
        if r.status_code == 200:
            d = r.json()
            if d.get('status') == 'success':
                lines.append(f"  Country    : {d.get('country','?')} ({d.get('countryCode','?')})")
                lines.append(f"  Region     : {d.get('regionName','?')} ({d.get('region','?')})")
                lines.append(f"  City       : {d.get('city','?')}")
                lines.append(f"  ZIP        : {d.get('zip','?')}")
                lines.append(f"  Lat/Lon    : {d.get('lat','?')} / {d.get('lon','?')}")
                lines.append(f"  Timezone   : {d.get('timezone','?')}")
                lines.append(f"  ISP        : {d.get('isp','?')}")
                lines.append(f"  ORG        : {d.get('org','?')}")
                lines.append(f"  AS         : {d.get('as','?')}")
                lines.append(f"  AS Name    : {d.get('asname','?')}")
                lines.append(f"  Mobile     : {d.get('mobile','?')}")
                lines.append(f"  Proxy/VPN  : {d.get('proxy','?')}")
                lines.append(f"  Hosting    : {d.get('hosting','?')}")
            else:
                lines.append(f"  [-] {d.get('message','API failed')}")
    except Exception as e:
        lines.append(f"  [-] GeoIP error: {e}")
    return lines

def reverse_dns(ip):
    lines = []
    try:
        host = socket.gethostbyaddr(ip)[0]
        lines.append(f"  Reverse DNS: {host}")
        try:
            ip2 = socket.gethostbyname(host)
            lines.append(f"  Forward chk: {host} -> {ip2}")
        except:
            pass
    except:
        lines.append("  Reverse DNS: None")
    return lines

def rdap_lookup(ip):
    lines = []
    try:
        r = http_get(f"https://rdap.arin.net/registry/ip/{ip}")
        if r.status_code == 200:
            data = r.json()
            if 'name' in data:
                lines.append(f"  Net Name   : {data.get('name','?')}")
            if 'handle' in data:
                lines.append(f"  Handle     : {data.get('handle','?')}")
            if 'entities' in data:
                for ent in data['entities'][:3]:
                    name = ent.get('vcardArray',[[],[]])[1][0][3] if len(ent.get('vcardArray',[[],[]])) > 1 else ent.get('handle','?')
                    lines.append(f"  Entity     : {name}")
            if 'events' in data:
                for ev in data['events']:
                    lines.append(f"  {ev.get('action','?').title()}: {ev.get('date','?')}")
        else:
            lines.append(f"  RDAP status: {r.status_code}")
    except:
        lines.append("  RDAP: Unavailable")
    return lines

def threat_intel(ip):
    lines = []
    # AbuseIPDB
    try:
        r = http_get(f"https://www.abuseipdb.com/check/{ip}")
        if r.status_code == 200 and "is not a known" not in r.text:
            lines.append("  [!] IP reported on AbuseIPDB")
    except:
        pass
    # VirusTotal
    try:
        r = http_get(f"https://www.virustotal.com/api/v3/ip_addresses/{ip}")
        if r.status_code == 200:
            data = r.json()
            stats = data.get('data',{}).get('attributes',{}).get('last_analysis_stats',{})
            if stats:
                lines.append(f"  VT Malicious: {stats.get('malicious',0)}")
                lines.append(f"  VT Suspicious: {stats.get('suspicious',0)}")
                lines.append(f"  VT Harmless : {stats.get('harmless',0)}")
        elif r.status_code == 401:
            lines.append("  VT: API key required")
    except:
        pass
    # Shodan
    try:
        r = http_get(f"https://internetdb.shodan.io/{ip}")
        if r.status_code == 200:
            data = r.json()
            if data.get('ports'):
                lines.append(f"  Shodan Ports: {', '.join(map(str, data['ports']))}")
            if data.get('hostnames'):
                lines.append(f"  Shodan Hosts: {', '.join(data['hostnames'][:5])}")
            if data.get('vulns'):
                lines.append(f"  Shodan Vulns: {', '.join(data['vulns'][:5])}")
    except:
        pass
    return lines

def port_check(ip):
    lines = []
    common = [22, 80, 443, 8080, 8443, 21, 3306, 3389, 5900, 27017]
    lines.append(f"  [Quick port scan (no confirm)]")
    lines.append(f"  Common ports: {', '.join(map(str, common))}")
    try:
        for port in common[:5]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((ip, port))
            if result == 0:
                lines.append(f"    Port {port}: OPEN")
            s.close()
    except:
        pass
    return lines

def run(ip):
    print(f"\n{'='*60}")
    print(f"  IP ADDRESS LOOKUP - Target: {ip}")
    print(f"{'='*60}")

    if not is_valid_ip(ip):
        print("  [!] Invalid IP address")
        return

    output = []

    print("\n  [Geolocation & ISP]")
    g = geo_lookup(ip)
    for l in g:
        print(l); output.append(l)

    print("\n  [DNS]")
    d = reverse_dns(ip)
    for l in d:
        print(l); output.append(l)

    print("\n  [RDAP/WHOIS]")
    r = rdap_lookup(ip)
    for l in r:
        print(l); output.append(l)

    print("\n  [Threat Intelligence]")
    t = threat_intel(ip)
    for l in t:
        print(l); output.append(l)

    print("\n  [Port Scan (quick)]")
    p = port_check(ip)
    for l in p:
        print(l); output.append(l)

    save_result("ip", ip, "\n".join(output))
