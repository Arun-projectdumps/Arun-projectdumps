"""Builds assets/stats.svg and assets/contributions.svg from GitHub data.
Runs in GitHub Actions (needs GH_TOKEN). Local preview: python3 live_stats.py --demo"""
import datetime as dt, json, os, sys, urllib.request
from html import escape as esc
from theme import window, prompt, GREEN, LIGHT, TEXT, DIM

USER = "Arun-projectdumps"
IGNORE = {"Shell", "Batchfile"}
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
Q = """query($login:String!){user(login:$login){
 followers{totalCount}
 repositories(ownerAffiliations:OWNER,first:100){totalCount nodes{isFork
   languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
 contributionsCollection{totalCommitContributions restrictedContributionsCount
   contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": Q, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GH_TOKEN']}", "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def demo():
    import random
    random.seed(4)
    start = dt.date.today() - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)
    weeks, d = [], start
    while d <= dt.date.today():
        weeks.append({"contributionDays": [{"date": str(d + dt.timedelta(i)), "contributionCount": random.choice([0, 0, 0, 1, 3, 7])}
                                           for i in range(7) if d + dt.timedelta(i) <= dt.date.today()]})
        d += dt.timedelta(7)
    langs = [("Python", 35), ("HTML", 20), ("TypeScript", 18), ("CSS", 13), ("Java", 6), ("C++", 4)]
    return {"followers": {"totalCount": 1},
            "repositories": {"totalCount": 15, "nodes": [{"isFork": False, "languages": {"edges": [{"size": s, "node": {"name": n}} for n, s in langs]}}]},
            "contributionsCollection": {"totalCommitContributions": 384, "restrictedContributionsCount": 0,
                                        "contributionCalendar": {"totalContributions": 384, "weeks": weeks}}}


def streaks(days):
    best = cur = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        best = max(best, run)
    for d in reversed(days):
        if d["contributionCount"]:
            cur += 1
        elif d is days[-1]:
            continue  # today not committed yet doesn't break the streak
        else:
            break
    return cur, best


def stats_svg(u):
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cur, best = streaks(days)
    sizes = {}
    for r in u["repositories"]["nodes"]:
        if r["isFork"]:
            continue
        for e in r["languages"]["edges"]:
            if e["node"]["name"] not in IGNORE:
                sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    total = sum(sizes.values()) or 1
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    rows = [("contributions (1y)", cc["contributionCalendar"]["totalContributions"]),
            ("commits (1y)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
            ("repositories", u["repositories"]["totalCount"]),
            ("followers", u["followers"]["totalCount"]),
            ("current streak", f"{cur} day{'s' * (cur != 1)}"),
            ("best streak", f"{best} day{'s' * (best != 1)}")]
    out = [prompt(24, 62, "./stats --live"),
           f'<text x="24" y="98" font-size="15" fill="{DIM}">// activity</text>',
           f'<text x="470" y="98" font-size="15" fill="{DIM}">// languages</text>',
           f'<line x1="445" y1="84" x2="445" y2="300" stroke="{GREEN}" stroke-opacity=".2"/>']
    for i, (k, v) in enumerate(rows):
        y = 130 + i * 30
        out.append(f'<text x="24" y="{y}" font-size="16" fill="{TEXT}">{esc(k)} <tspan fill="#30363d">{"." * (22 - len(k))}</tspan> '
                   f'<tspan fill="{GREEN}" font-weight="700">{esc(str(v))}</tspan></text>')
    for i, (name, size) in enumerate(top):
        y, pct = 130 + i * 30, size * 100 / total
        filled = max(1, round(pct / 5))
        out.append(f'<text x="470" y="{y}" font-size="15" fill="{TEXT}">{esc(name)}</text>')
        for b in range(20):
            out.append(f'<rect x="{590 + b*11}" y="{y-12}" width="9" height="13" fill="{GREEN if b < filled else "#0b3d1a"}"/>')
        out.append(f'<text x="876" y="{y}" font-size="14" fill="{LIGHT}" text-anchor="end">{pct:.0f}%</text>')
    stamp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)
    out.append(f'<text x="876" y="318" font-size="11" fill="#484f58" text-anchor="end">updated {stamp:%d %b %Y, %H:%M} IST</text>')
    return window(900, 332, "~/arun — stats", "\n".join(out))


def contrib_svg(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    shades = ["#161b22", "#0b4a1f", "#0f7a2e", "#1fc24a", "#00ff41"]
    mx = max([d["contributionCount"] for w in weeks for d in w["contributionDays"]] + [1])
    cell, gap, x0, y0 = 13, 3, 46, 112
    out = [prompt(24, 62, "git log --graph --since=1.year"),
           f'<text x="24" y="88" font-size="14" fill="{DIM}">{cal["totalContributions"]} contributions in the last year</text>']
    for i, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{x0-8}" y="{y0 + i*(cell+gap) + 11}" font-size="10" fill="{DIM}" text-anchor="end">{lab}</text>')
    last_month = None
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            date = dt.date.fromisoformat(d["date"])
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / mx))
            out.append(f'<rect x="{x0 + wi*(cell+gap)}" y="{y0 + ((date.weekday()+1) % 7)*(cell+gap)}" width="{cell}" height="{cell}" fill="{shades[lvl]}"/>')
            if date.day <= 7 and date.month != last_month and (date.weekday() + 1) % 7 == 0:
                last_month = date.month
                out.append(f'<text x="{x0 + wi*(cell+gap)}" y="{y0-8}" font-size="10" fill="{DIM}">{date:%b}</text>')
    ly = y0 + 7 * (cell + gap) + 18
    out.append(f'<text x="{x0 + 53*(cell+gap) - 130}" y="{ly+10}" font-size="10" fill="{DIM}" text-anchor="end">less</text>')
    for i, s in enumerate(shades):
        out.append(f'<rect x="{x0 + 53*(cell+gap) - 124 + i*17}" y="{ly}" width="13" height="13" fill="{s}"/>')
    out.append(f'<text x="{x0 + 53*(cell+gap) - 34}" y="{ly+10}" font-size="10" fill="{DIM}">more</text>')
    return window(900, ly + 32, "~/arun — git log", "\n".join(out))


if __name__ == "__main__":
    u = demo() if "--demo" in sys.argv else fetch()
    dest = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else OUT
    open(os.path.join(dest, "stats.svg"), "w").write(stats_svg(u))
    open(os.path.join(dest, "contributions.svg"), "w").write(contrib_svg(u))
    print("ok")
