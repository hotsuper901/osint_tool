#!/usr/bin/env python3

import os
import sys
import time
import signal

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.style import Style
from rich import print as rprint

from ascii_art import (
    print_banner, print_menu_table, print_result_header,
    print_section, print_found, print_info, print_warn, print_error,
    CREATOR, C1, C2, C3, C4, C5, C6
)
from modules import (
    email_lookup, ip_lookup, domain_info, phone_lookup,
    username_search, port_scanner, social_media, url_scanner
)

console = Console()

MENU_ITEMS = [
    ("1",  "Email Lookup",            email_lookup),
    ("2",  "IP Address Lookup",       ip_lookup),
    ("3",  "Domain Information",      domain_info),
    ("4",  "Phone Number Lookup",     phone_lookup),
    ("5",  "Username Search (30+)",    username_search),
    ("6",  "Port Scanner",            port_scanner),
    ("7",  "Social Media Profiler",    social_media),
    ("8",  "URL / Link Scanner",      url_scanner),
    ("0",  "Exit",                    None),
]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def handler(sig, frame):
    console.print(f"\n\n[bold {C5}][!] Exiting OSINT MAX Toolkit by {CREATOR}...[/]")
    sys.exit(0)

def run_module(module, label):
    clear()
    print_banner()
    target = Prompt.ask(f"\n[bold {C4}][>][/] Enter target for [bold {C3}]{label}[/]")
    if target:
        module.run(target)
    else:
        print_error("No input provided.")
    input(f"\n  [{C2}][+][/] Press Enter to return to menu...")

def main():
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    while True:
        clear()
        print_banner()
        print_menu_table(MENU_ITEMS)

        choice = Prompt.ask(
            f"\n[bold {C4}][>][/] Select option [bold {C3}][0-{len(MENU_ITEMS)-1}][/]"
        )

        if choice == "0":
            console.print(
                f"\n[bold {C1}][+] Thank you for using OSINT MAX Toolkit by {CREATOR}![/]"
            )
            console.print(f"[bold {C1}][+] Stay safe & ethical.[/]\n")
            sys.exit(0)

        matched = False
        for key, name, module in MENU_ITEMS:
            if choice == key and module:
                run_module(module, name)
                matched = True
                break

        if not matched:
            console.print(f"\n[bold {C5}][!] Invalid option.[/]")
            time.sleep(1)

if __name__ == "__main__":
    main()
