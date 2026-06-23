import os
import json
import math
import urllib.request
import urllib.error
from datetime import datetime, timezone

USERNAME = "Bhishy3"
TOKEN = os.environ.get("GH_TOKEN", "")

def gh(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": USERNAME
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def graphql(query):
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=data,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": USERNAME
        }
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

user = gh(f"/users/{USERNAME}")

gql = graphql(f"""
{{
  user(login: "{USERNAME}") {{
    contributionsCollection {{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
      contributionCalendar {{
        totalContributions
        weeks {{
          contributionDays {{
            contributionCount
            date
          }}
        }}
      }}
    }}
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {{
      nodes {{
        stargazerCount
        primaryLanguage {{ name }}
        languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
          edges {{
            size
            node {{ name color }}
          }}
        }}
      }}
    }}
    pullRequests {{ totalCount }}
    issues {{ totalCount }}
  }}
}}
""")

u = gql["data"]["user"]
cc = u["contributionsCollection"]
repos_data = u["repositories"]["nodes"]

total_commits = cc["totalCommitContributions"]
total_prs = u["pullRequests"]["totalCount"]
total_issues = u["issues"]["totalCount"]
total_stars = sum(r["stargazerCount"] for r in repos_data)
followers = user["followers"]
public_repos = user["public_repos"]
created_at = user["created_at"]
account_age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(created_at.replace("Z", "+00:00"))).days

lang_sizes = {}
for repo in repos_data:
    for edge in repo.get("languages", {}).get("edges", []):
        name = edge["node"]["name"]
        color = edge["node"].get("color") or "#3ecf74"
        size = edge["size"]
        if name not in lang_sizes:
            lang_sizes[name] = {"size": 0, "color": color}
        lang_sizes[name]["size"] += size

total_lang_size = sum(v["size"] for v in lang_sizes.values()) or 1
lang_pcts = sorted(
    [{"name": k, "pct": round(v["size"] / total_lang_size * 100, 1), "color": v["color"]}
     for k, v in lang_sizes.items()],
    key=lambda x: -x["pct"]
)[:6]

score = (
    min(commits_score := min(total_commits / 200, 1) * 35, 35) +
    min(pr_score := min(total_prs / 50, 1) * 20, 20) +
    min(star_score := min(total_stars / 20, 1) * 15, 15) +
    min(follower_score := min(followers / 20, 1) * 15, 15) +
    min(repo_score := min(public_repos / 10, 1) * 10, 10) +
    min(age_score := min(account_age_days / 365, 1) * 5, 5)
)
score_pct = round(score)

if score_pct >= 90: grade = "A+"
elif score_pct >= 80: grade = "A"
elif score_pct >= 70: grade = "B+"
elif score_pct >= 60: grade = "B"
elif score_pct >= 50: grade = "C+"
elif score_pct >= 40: grade = "C"
else: grade = "D"

weeks = cc["contributionCalendar"]["weeks"]
all_days = [d for w in weeks for d in w["contributionDays"]]
recent_52 = all_days[-364:] if len(all_days) >= 364 else all_days
max_contrib = max((d["contributionCount"] for d in recent_52), default=1) or 1

def contrib_level(n):
    if n == 0: return 0
    if n <= max_contrib * 0.25: return 1
    if n <= max_contrib * 0.55: return 2
    if n <= max_contrib * 0.80: return 3
    return 4

level_colors = ["#0a2e18", "#1b5e32", "#2d9e6b", "#3ecf74", "#6effa0"]

streak = 0
best_streak = 0
cur = 0
for day in reversed(recent_52):
    if day["contributionCount"] > 0:
        cur += 1
        best_streak = max(best_streak, cur)
        if streak == 0:
            streak = cur
    else:
        if streak > 0:
            break
        cur = 0

W, H = 860, 620
circ = 2 * math.pi * 52
arc_fill = circ * (score_pct / 100)
arc_offset = circ - arc_fill

bar_items = [
    ("Commits", min(100, round(total_commits / 200 * 100)), "#3ecf74"),
    ("Pull Requests", min(100, round(total_prs / 50 * 100)), "#4db8ff"),
    ("Stars", min(100, round(total_stars / 20 * 100)), "#3ecf74"),
    ("Issues", min(100, round(total_issues / 30 * 100)), "#4db8ff"),
]

CELL = 11
GAP = 3
GRID_COLS = 52
GRID_ROWS = 7
grid_w = GRID_COLS * (CELL + GAP) - GAP
grid_x = (W - grid_w) // 2
grid_y = 490

svg_lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs>',
    '  <style>',
    '    @import url("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap");',
    '    text { font-family: "JetBrains Mono", monospace; }',
    '    .anim-arc { animation: fillArc 1.5s ease-out forwards; }',
    '    @keyframes fillArc {',
    f'      from {{ stroke-dashoffset: {circ:.1f}; }}',
    f'      to   {{ stroke-dashoffset: {arc_offset:.1f}; }}',
    '    }',
    '    .anim-bar { animation: growBar 1.2s ease-out forwards; }',
    '    @keyframes growBar { from { width: 0; } }',
    '  </style>',
    '</defs>',
    f'<rect width="{W}" height="{H}" fill="#060f09" rx="12"/>',
    f'<path d="M0,{H} L0,80 C{W*0.1:.0f},55 {W*0.25:.0f},105 {W*0.4:.0f},80 C{W*0.55:.0f},55 {W*0.7:.0f},40 {W*0.85:.0f},62 L{W},{H*0.45:.0f} Z" fill="#0a3d1f"/>',
    f'<path d="M0,{H} L0,115 C{W*0.15:.0f},92 {W*0.35:.0f},138 {W*0.5:.0f},115 C{W*0.65:.0f},92 {W*0.8:.0f},105 {W},98 Z" fill="#145a2e"/>',
    f'<path d="M0,{H} L0,148 C{W*0.2:.0f},128 {W*0.45:.0f},162 {W*0.6:.0f},145 C{W*0.75:.0f},128 {W*0.9:.0f},138 {W},132 Z" fill="#1b6b38"/>',
    '<image href="https://github.com/Bhishy3.png" x="370" y="18" width="60" height="60" clip-path="circle(30px at 30px 30px)" style="border-radius:50%;"/>',
    '<text x="440" y="44" fill="#c8f0d8" font-size="20" font-weight="500">Bhishan Charitra</text>',
    '<text x="440" y="66" fill="#6dbe8c" font-size="12">Aspiring Mechatronics Engineer · Melbourne, AU</text>',
    '<line x1="40" y1="98" x2="820" y2="98" stroke="#1b4332" stroke-width="0.5"/>',
]

GX, GY = 60, 118
svg_lines += [
    f'<text x="{GX}" y="{GY}" fill="#4a7a5a" font-size="10" letter-spacing="2">GITHUB SCORE</text>',
    f'<circle cx="{GX+52}" cy="{GY+70}" r="52" fill="none" stroke="#1b4332" stroke-width="7"/>',
    f'<circle cx="{GX+52}" cy="{GY+70}" r="52" fill="none" stroke="#3ecf74" stroke-width="7"',
    f'  stroke-dasharray="{circ:.1f}" stroke-dashoffset="{arc_offset:.1f}"',
    f'  stroke-linecap="round" transform="rotate(-90 {GX+52} {GY+70})" class="anim-arc"/>',
    f'<text x="{GX+52}" y="{GY+64}" fill="#c8f0d8" font-size="22" font-weight="500" text-anchor="middle">{grade}</text>',
    f'<text x="{GX+52}" y="{GY+82}" fill="#4a7a5a" font-size="9" text-anchor="middle">{score_pct}%</text>',
]

bx, by = GX + 130, GY + 10
for i, (name, pct, color) in enumerate(bar_items):
    y = by + i * 36
    bar_w = max(4, round(pct / 100 * 220))
    svg_lines += [
        f'<text x="{bx}" y="{y+13}" fill="#6dbe8c" font-size="11">{name}</text>',
        f'<rect x="{bx}" y="{y+18}" width="220" height="5" rx="2" fill="#1b4332"/>',
        f'<rect x="{bx}" y="{y+18}" width="{bar_w}" height="5" rx="2" fill="{color}"/>',
        f'<text x="{bx+228}" y="{y+24}" fill="#4a7a5a" font-size="10">{pct}%</text>',
    ]

sx, sy = 460, GY
stats = [
    ("ti-git-commit", str(total_commits), "Commits"),
    ("ti-git-pull-request", str(total_prs), "Pull Requests"),
    ("ti-star", str(total_stars), "Stars"),
    ("ti-users", str(followers), "Followers"),
    ("ti-flame", str(streak), "Day Streak"),
    ("ti-box", str(public_repos), "Repos"),
]
for i, (_, val, label) in enumerate(stats):
    col = i % 3
    row = i // 3
    cx2 = sx + col * 130
    cy2 = sy + row * 70
    svg_lines += [
        f'<rect x="{cx2}" y="{cy2}" width="118" height="58" rx="8" fill="#051a0d" stroke="#1b4332" stroke-width="0.5"/>',
        f'<text x="{cx2+12}" y="{cy2+28}" fill="#c8f0d8" font-size="20" font-weight="500">{val}</text>',
        f'<text x="{cx2+12}" y="{cy2+44}" fill="#4a7a5a" font-size="10">{label}</text>',
    ]

lx, ly = 60, 290
svg_lines.append(f'<text x="{lx}" y="{ly}" fill="#4a7a5a" font-size="10" letter-spacing="2">TOP LANGUAGES</text>')
ly += 16
for i, lang in enumerate(lang_pcts):
    bar_w = max(4, round(lang["pct"] / 100 * 340))
    color = lang["color"] if lang["color"] != "#" else "#3ecf74"
    svg_lines += [
        f'<circle cx="{lx+6}" cy="{ly+i*26+6}" r="5" fill="{color}"/>',
        f'<text x="{lx+18}" y="{ly+i*26+11}" fill="#a8e6c0" font-size="12">{lang["name"]}</text>',
        f'<rect x="{lx+160}" y="{ly+i*26+3}" width="340" height="5" rx="2" fill="#1b4332"/>',
        f'<rect x="{lx+160}" y="{ly+i*26+3}" width="{bar_w}" height="5" rx="2" fill="{color}"/>',
        f'<text x="{lx+508}" y="{ly+i*26+11}" fill="#4a7a5a" font-size="11">{lang["pct"]}%</text>',
    ]

for i, (day_group) in enumerate([d for d in recent_52]):
    col = i // 7
    row = i % 7
    count = day_group["contributionCount"]
    lvl = contrib_level(count)
    cx3 = grid_x + col * (CELL + GAP)
    cy3 = grid_y + row * (CELL + GAP)
    svg_lines.append(f'<rect x="{cx3}" y="{cy3}" width="{CELL}" height="{CELL}" rx="2" fill="{level_colors[lvl]}"/>')

svg_lines += [
    f'<text x="{W//2}" y="{grid_y + GRID_ROWS*(CELL+GAP) + 16}" fill="#4a7a5a" font-size="10" text-anchor="middle" letter-spacing="2">CONTRIBUTION ACTIVITY · LAST 52 WEEKS</text>',
    '</svg>'
]

svg_output = "\n".join(svg_lines)
os.makedirs("assets", exist_ok=True)
with open("assets/stats.svg", "w") as f:
    f.write(svg_output)

print(f"Generated stats.svg — Grade: {grade} ({score_pct}%), Commits: {total_commits}, Stars: {total_stars}")
