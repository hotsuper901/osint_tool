# OSINT MAXIMUM TOOLKIT

Creator: **M.S.J**

A modular OSINT (Open Source Intelligence) toolkit with 8 modules for information gathering.

## Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | Email Lookup | SPF/DMARC records, breach check (HIBP), paste dumps, EmailRep reputation, Gravatar, social profile discovery |
| 2 | IP Address Lookup | IP geolocation, ISP, ASN, threat intelligence |
| 3 | Domain Information | WHOIS, DNS records, SSL certificate info |
| 4 | Phone Number Lookup | Carrier, location, line type |
| 5 | Username Search (30+) | Cross-platform username search on 30+ sites |
| 6 | Port Scanner | Common port scanning on target host |
| 7 | Social Media Profiler | Profile analysis from social platforms |
| 8 | URL / Link Scanner | URL safety check, redirect tracing |

## Requirements

- Python 3.8+
- `rich` - Terminal UI
- `pyfiglet` - Banner
- `requests` - HTTP requests
- `dnspython` - DNS lookups

## Installation

```bash
git clone
https://github.com/hotsuper901/osint_tool.git
cd osint_tool
pip install -r requirements.txt
python3 main.py
```

## Usage

Run the toolkit:

```bash
python3 main.py
```

Select a module by entering its number. Follow the prompts to input your target.

## Notes

This tool is for educational and authorized security research only. The creator is not responsible for any misuse.
