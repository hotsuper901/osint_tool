import re
import json
import dns.resolver
import hashlib
from utils import http_get, is_valid_email, save_result

def check_spf_dmarc(domain):
    lines = []
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            txt = str(rdata)
            if txt.startswith('"v=spf'):
                lines.append(f"    SPF: {txt}")
            elif 'v=DMARC' in txt or txt.startswith('"v=DMARC'):
                for a in dns.resolver.resolve(f'_dmarc.{domain}', 'TXT'):
                    lines.append(f"    DMARC: {str(a)}")
    except:
        lines.append("    No SPF/DMARC records found")
    return lines

def check_breaches(email):
    lines = []
    try:
        r = http_get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}")
        if r.status_code == 200:
            breaches = r.json()
            lines.append(f"  [!] Breaches: {len(breaches)}")
            for b in breaches[:10]:
                lines.append(f"      - {b['Title']} ({b.get('BreachDate','?')}) - {b.get('PwnCount','?')} accounts")
            if len(breaches) > 10:
                lines.append(f"      ... and {len(breaches)-10} more")
        elif r.status_code == 404:
            lines.append("  [+] No known breaches (HIBP)")
        else:
            lines.append(f"  [-] HIBP status: {r.status_code}")
    except:
        lines.append("  [-] Breach check unavailable")
    return lines

def check_pastes(email):
    lines = []
    try:
        r = http_get(f"https://psbdmp.ws/api/v3/search?q={email}")
        if r.status_code == 200:
            data = r.json()
            count = data.get('count', data.get('total', 0))
            lines.append(f"  [+] Pastebin dumps: {count}")
        else:
            lines.append(f"  [-] Paste check status: {r.status_code}")
    except:
        pass
    return lines

def check_emailrep(email):
    lines = []
    try:
        r = http_get("https://emailrep.io/" + email, headers={"User-Agent": "OSINT-MAX"})
        if r.status_code == 200:
            d = r.json()
            lines.append(f"  [i] EmailRep.io:")
            lines.append(f"      Reputation : {d.get('reputation','?')}")
            lines.append(f"      Suspicious : {d.get('suspicious','?')}")
            lines.append(f"      Details    : {json.dumps(d.get('details',{}), indent=6)}")
    except:
        pass
    return lines

def check_gravatar(email):
    lines = []
    md5 = hashlib.md5(email.lower().encode()).hexdigest()
    url = f"https://www.gravatar.com/avatar/{md5}?d=404&s=400"
    try:
        r = http_get(url)
        if r.status_code == 200:
            lines.append(f"  [+] Gravatar: https://www.gravatar.com/{md5}")
            try:
                r2 = http_get(f"https://www.gravatar.com/{md5}.json")
                if r2.status_code == 200:
                    prof = r2.json()
                    entry = prof.get('entry', [{}])[0]
                    if 'name' in entry:
                        lines.append(f"      Name: {entry['name'].get('formatted','?')}")
                    if 'profileUrl' in entry:
                        lines.append(f"      Profile: {entry['profileUrl']}")
                    if 'accounts' in entry:
                        for ac in entry['accounts']:
                            lines.append(f"      {ac.get('domain','?')}: {ac.get('url','?')}")
            except:
                pass
    except:
        pass
    return lines

def check_google_social(email):
    lines = []
    username = email.split('@')[0]
    domain = email.split('@')[1]
    lines.append(f"  [i] Possible profiles for '{username}':")
    platforms = [
        ("GitHub", f"https://github.com/{username}"),
        ("Twitter", f"https://twitter.com/{username}"),
        ("LinkedIn", f"https://www.linkedin.com/in/{username}"),
        ("Facebook", f"https://www.facebook.com/{username}"),
        ("Instagram", f"https://instagram.com/{username}"),
        ("Reddit", f"https://reddit.com/user/{username}"),
    ]
    for name, url in platforms:
        try:
            r = http_get(url, timeout=3)
            if r.status_code == 200:
                lines.append(f"      {name}: {url}")
        except:
            pass
    return lines

def run(email):
    print(f"\n{'='*60}")
    print(f"  EMAIL LOOKUP - Target: {email}")
    print(f"{'='*60}")

    if not is_valid_email(email):
        print("  [!] Invalid email format")
        return

    username, domain = email.split('@')
    output_lines = []
    output_lines.append(f"Username: {username}")
    output_lines.append(f"Domain:   {domain}")

    print(f"\n  [i] Username : {username}")
    print(f"  [i] Domain   : {domain}")
    print()

    print("  [SPF/DMARC Records]")
    spf_lines = check_spf_dmarc(domain)
    for l in spf_lines:
        print(l)
        output_lines.append(l)

    print("\n  [Breach Check - HIBP]")
    breach_lines = check_breaches(email)
    for l in breach_lines:
        print(l)
        output_lines.append(l)

    print("\n  [Paste Dumps]")
    paste_lines = check_pastes(email)
    for l in paste_lines:
        print(l)
        output_lines.append(l)

    print("\n  [EmailRep Reputation]")
    rep_lines = check_emailrep(email)
    for l in rep_lines:
        print(l)
        output_lines.append(l)

    print("\n  [Gravatar]")
    grav_lines = check_gravatar(email)
    for l in grav_lines:
        print(l)
        output_lines.append(l)

    print("\n  [Social Profile Discovery]")
    soc_lines = check_google_social(email)
    for l in soc_lines:
        print(l)
        output_lines.append(l)

    save_result("email", email, "\n".join(output_lines))
