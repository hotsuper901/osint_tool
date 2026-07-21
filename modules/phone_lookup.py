import re
import json
from utils import http_get, save_result

def validate_phone(phone):
    cleaned = re.sub(r'[\s\-\(\)\+\.]', '', phone)
    if cleaned.isdigit() and 7 <= len(cleaned) <= 15:
        return cleaned
    return None

def detect_country(phone):
    lines = []
    try:
        r = http_get(f"https://phonevalidation.abstractapi.com/v1/?api_key=&phone={phone}")
        if r.status_code == 200:
            d = r.json()
            if d.get('valid'):
                lines.append(f"  Valid       : Yes")
                lines.append(f"  Country     : {d.get('country',{}).get('name','?')} ({d.get('country',{}).get('code','?')})")
                lines.append(f"  Location    : {d.get('location','?')}")
                lines.append(f"  Carrier     : {d.get('carrier','?')}")
                lines.append(f"  Line Type   : {d.get('line_type','?')}")
                lines.append(f"  Format Intl : {d.get('format',{}).get('international','?')}")
                lines.append(f"  Format Local: {d.get('format',{}).get('local','?')}")
            else:
                lines.append(f"  Valid       : No - {d.get('error',{}).get('message','')}")
        else:
            lines.append("  AbstractAPI: No key (limited)")
    except:
        lines.append("  Validation API unavailable")
    return lines

def check_reputation(phone):
    lines = []
    try:
        r = http_get(f"https://www.numlookup.com/{phone}")
        if r.status_code == 200:
            if "Spam" in r.text:
                lines.append("  [!] Possible spam/scam reports found")
            else:
                lines.append("  [+] No spam reports detected")
    except:
        pass
    return lines

def google_search_links(phone):
    lines = []
    lines.append(f"  Google      : https://www.google.com/search?q={phone}")
    lines.append(f"  Truecaller  : https://www.truecaller.com/search/in/{phone}")
    lines.append(f"  SpyDialer   : https://www.spydialer.com/default.aspx")
    lines.append(f"  Zlookup     : https://www.zlookup.com/phone/{phone}")
    lines.append(f"  WhoCallsMe  : https://whocallsme.com/Phone-Number.aspx/{phone}")
    lines.append(f"  SyncMe      : https://www.sync.me/")
    return lines

def reverse_lookup_tools(phone):
    lines = []
    lines.append("  [Manual Search Suggestions]")
    lines.append(f"  Search in social media: https://www.facebook.com/search/top/?q={phone}")
    lines.append(f"  WhatsApp link: https://wa.me/{phone}")
    lines.append(f"  Telegram: https://t.me/+{phone}")
    lines.append(f"  Viber: https://viber://add?number={phone}")
    return lines

def run(phone):
    print(f"\n{'='*60}")
    print(f"  PHONE NUMBER LOOKUP - Target: {phone}")
    print(f"{'='*60}")

    cleaned = validate_phone(phone)
    if not cleaned:
        print("  [!] Invalid phone number (must be 7-15 digits)")
        return

    output = [f"Cleaned: {cleaned}"]
    print(f"\n  [i] Cleaned number: {cleaned}")

    print("\n  [Validation & Carrier]")
    v = detect_country(cleaned)
    for l in v:
        print(l); output.append(l)

    print("\n  [Reputation Check]")
    r = check_reputation(cleaned)
    for l in r:
        print(l); output.append(l)

    print("\n  [Direct Links]")
    g = google_search_links(cleaned)
    for l in g:
        print(l); output.append(l)

    print("\n  [Social/App Links]")
    s = reverse_lookup_tools(cleaned)
    for l in s:
        print(l); output.append(l)

    save_result("phone", phone, "\n".join(output))
