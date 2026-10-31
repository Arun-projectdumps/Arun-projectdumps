"""Builds the static README graphics (project cards, stack, footer). Run: python3 scripts/static_assets.py"""
import os, textwrap
from html import escape as esc
from theme import window, prompt, GREEN, LIGHT, TEXT, DIM

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

PROJECTS = [
    ("ultron", "macOS (Apple Silicon) app: a real zsh terminal in a cinematic UI for launching Claude Code", "Tauri 2 · React · TypeScript · Rust · xterm.js"),
    ("Claude-skills-", "A collection of useful Claude skills you can add to your own setup", "Claude · Markdown"),
    ("attendance-mangmnet-system", "Attendance management system", "Java · HTML"),
    ("Leetcode-Problems-daily", "Daily LeetCode solutions, synced with LeetHub", "C++ · Java"),
]

STACK = [
    ("languages", ["Java", "C++", "Python", "TypeScript", "JavaScript", "Rust", "HTML5", "CSS3", "Shell"]),
    ("tools", ["React", "Tauri", "xterm.js", "macOS", "Claude Code", "Git", "LeetCode"]),
]


def card(name, desc, stack):
    w, h = 440, 170
    lines = textwrap.wrap(desc, 44)[:3]
    body = [f'<text x="20" y="58" font-size="19" font-weight="700" fill="{GREEN}">&gt; {esc(name)}</text>']
    body += [f'<text x="20" y="{88 + i*20}" font-size="14" fill="{TEXT}">{esc(l)}</text>' for i, l in enumerate(lines)]
    body.append(f'<text x="20" y="152" font-size="13" fill="{LIGHT}">[ {esc(stack)} ]</text>')
    return window(w, h, f"~/projects/{name}", "\n".join(body))


def stack():
    w, x0, out, y = 900, 24, [prompt(24, 62, "cat ~/stack.txt")], 100
    for label, items in STACK:
        out.append(f'<text x="{x0}" y="{y}" font-size="15" fill="{DIM}">{label}:</text>')
        x = x0 + 120
        for it in items:
            tw = len(it) * 9 + 22
            if x + tw > w - 20:
                x, y = x0 + 120, y + 40
            out.append(f'<rect x="{x}" y="{y-19}" width="{tw}" height="28" fill="#0b3d1a" stroke="{GREEN}" stroke-opacity=".7"/>'
                       f'<text x="{x + tw/2}" y="{y}" font-size="15" fill="{GREEN}" text-anchor="middle">{esc(it)}</text>')
            x += tw + 10
        y += 52
    return window(w, y - 10, "~/arun — stack", "\n".join(out))


def footer():
    body = (prompt(24, 60, "exit") +
            f'<text x="24" y="90" font-size="15" fill="{DIM}">[ connection closed ] thanks for visiting — see you in the next commit</text>')
    return window(900, 112, "~/arun — logout", body)


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "projects"), exist_ok=True)
    for p in PROJECTS:
        open(os.path.join(OUT, "projects", f"{p[0]}.svg"), "w").write(card(*p))
    open(os.path.join(OUT, "stack.svg"), "w").write(stack())
    open(os.path.join(OUT, "footer.svg"), "w").write(footer())
    print("ok")
