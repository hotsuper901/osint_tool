import socket
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style
from rich import box


CREATOR = "M.S.J"
console = Console()

C1 = "#00FF87"
C2 = "#60EFFF"
C3 = "#FF00E5"
C4 = "#FFB800"
C5 = "#FF6B6B"
C6 = "#7C3AED"

def print_banner():
    host = socket.gethostname()
    title = Text()
    title.append("██╗  ██╗ ██████╗ ███████╗██╗███╗   ██╗████████╗", style=f"bold {C1}")
    title.append("\n")
    title.append("╚██╗██╔╝██╔═══██╗╚══██╔══╝██║████╗  ██║╚══██╔══╝", style=f"bold {C2}")
    title.append("\n")
    title.append(" ╚███╔╝ ██║   ██║   ██║   ██║██╔██╗ ██║   ██║   ", style=f"bold {C3}")
    title.append("\n")
    title.append(" ██╔██╗ ██║   ██║   ██║   ██║██║╚██╗██║   ██║   ", style=f"bold {C4}")
    title.append("\n")
    title.append("██╔╝ ██╗╚██████╔╝   ██║   ██║██║ ╚████║   ██║   ", style=f"bold {C5}")
    title.append("\n")
    title.append("╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═══╝   ╚═╝   ", style=f"bold {C6}")

    subtitle = Text(
        f"Open Source Intelligence Toolkit | Creator: {CREATOR} | Host: {host}",
        style=f"italic {C2}"
    )

    inner = Text.assemble(
        ("\n", ""),
        title,
        ("\n", ""),
        (f"Maximum Edition - All modules loaded", f"bold {C4}"),
        ("\n", ""),
        subtitle,
    )
    panel = Panel(
        inner,
        box=box.HEAVY,
        border_style=Style(color=C1),
        padding=(1, 4),
        title=f"[bold {C4}]OSINT MAXIMUM TOOLKIT[/]",
        subtitle=f"[italic {C2}]Creator: {CREATOR}[/]",
    )
    console.print(panel)

def print_menu_table(menu_items):
    table = Table(
        show_header=True,
        header_style=f"bold {C4}",
        border_style=C1,
        box=box.HEAVY_EDGE,
        title=f"[bold {C3}]╔══ MAIN MENU ══╗[/]",
        title_style=f"bold {C4}",
        title_justify="center",
    )
    table.add_column("#", style=f"bold {C6}", width=5, justify="center")
    table.add_column("Module", style="white", min_width=30)

    for key, name, _ in menu_items:
        if key == "0":
            row_style = f"dim {C5}"
        else:
            row_style = f"bold {C1}"
        table.add_row(key, f"[{row_style}]{name}[/]")

    console.print(table)

def print_result_header(title, target):
    console.print(Panel(
        f"[bold {C4}]{title}[/]\n[bold {C1}]Target:[/] [white]{target}[/]",
        box=box.HEAVY,
        border_style=C3,
        padding=(0, 2)
    ))

def print_section(name):
    console.print(f"\n[bold {C4}]◆ {name}[/]")

def print_found(text):
    console.print(f"  [bold {C1}]✔[/] {text}")

def print_info(text):
    console.print(f"  [bold {C2}]ℹ[/] {text}")

def print_warn(text):
    console.print(f"  [bold {C5}]⚠[/] {text}")

def print_error(text):
    console.print(f"  [bold red]✘[/] {text}")

def print_header():
    panel = Panel(
        f"[bold {C3}]OSINT MAXIMUM TOOLKIT[/]\n[{C2}]Creator: {CREATOR}[/]",
        box=box.HEAVY,
        border_style=C4,
        padding=(1, 2)
    )
    console.print(panel)
