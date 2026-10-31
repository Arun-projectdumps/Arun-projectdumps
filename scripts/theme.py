"""Shared terminal/cyber look for every README graphic."""
from html import escape as esc

FONT = "'Courier New', Consolas, 'DejaVu Sans Mono', monospace"
BG, BAR, GREEN, LIGHT, TEXT, DIM = "#0d1117", "#161b22", "#00ff41", "#7ee787", "#c9d1d9", "#8b949e"


def window(w, h, title, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">
<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>
<rect x="1" y="1" width="{w-2}" height="28" rx="10" fill="{BAR}"/>
<rect x="1" y="18" width="{w-2}" height="11" fill="{BAR}"/>
<line x1="1" y1="29" x2="{w-1}" y2="29" stroke="{GREEN}" stroke-opacity=".35"/>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="none" stroke="{GREEN}" stroke-opacity=".55"/>
<circle cx="20" cy="15" r="5.5" fill="#ff5f56"/><circle cx="38" cy="15" r="5.5" fill="#ffbd2e"/><circle cx="56" cy="15" r="5.5" fill="#27c93f"/>
<text x="{w/2}" y="20" fill="{DIM}" font-size="12" text-anchor="middle">{esc(title)}</text>
{body}
</svg>'''


def prompt(x, y, cmd, size=18):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{GREEN}">arun@projectdumps:~$ '
            f'<tspan fill="{TEXT}">{esc(cmd)}</tspan></text>')
