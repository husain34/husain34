import json
import urllib.request
import time
import re
import os

username = "husain34"
repos_url = f"https://api.github.com/users/{username}/repos"
user_url = f"https://api.github.com/users/{username}"
token = os.environ.get("GITHUB_TOKEN")

def get_request(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    if token:
        req.add_header('Authorization', f'token {token}')
    return req

req = get_request(user_url)
with urllib.request.urlopen(req) as response:
    user_data = json.loads(response.read().decode())
    
followers = user_data.get('followers', 0)
public_repos = user_data.get('public_repos', 0)

req = get_request(repos_url)
with urllib.request.urlopen(req) as response:
    repos = json.loads(response.read().decode())

total_commits = 0
total_additions = 0
total_deletions = 0
contributed_repos = 0
total_stars = 0

for repo in repos:
    repo_name = repo['name']
    total_stars += repo.get('stargazers_count', 0)
    stats_url = f"https://api.github.com/repos/{username}/{repo_name}/stats/contributors"
    req = get_request(stats_url)
    
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 202:
            time.sleep(2)
            response = urllib.request.urlopen(req)
        stats = json.loads(response.read().decode())
        if stats:
            contributed_repos += 1
            for author_stat in stats:
                total_commits += author_stat['total']
                for week in author_stat['weeks']:
                    total_additions += week['a']
                    total_deletions += week['d']
    except Exception as e:
        print(f"Error fetching stats for {repo_name}: {e}")

total_loc = total_additions + total_deletions

# --- UPDATE SVG ---
with open('profile.svg', 'r', encoding='utf-8') as f:
    svg_content = f.read()

# 1. Repos & Contributed
svg_content = re.sub(
    r'<tspan fill="#8b949e">\d+ \{Contributed: \d+\}</tspan><tspan fill="#484f58"> \| ',
    f'<tspan fill="#8b949e">{public_repos} {{Contributed: {contributed_repos}}}</tspan><tspan fill="#484f58"> | ',
    svg_content
)

# 2. Stars
svg_content = re.sub(
    r'</tspan><tspan fill="#c9d1d9">Stars:</tspan> <tspan fill="#484f58">\.\.\.\.\.\.</tspan> <tspan fill="#8b949e">\d+</tspan></text>',
    f'</tspan><tspan fill="#c9d1d9">Stars:</tspan> <tspan fill="#484f58">......</tspan> <tspan fill="#8b949e">{total_stars}</tspan></text>',
    svg_content
)

# 3. Commits
svg_content = re.sub(
    r'</tspan><tspan fill="#c9d1d9">Commits:</tspan> <tspan fill="#484f58">\.\.\.\.\.\.\.\.\.\.\.\.\.\.</tspan> <tspan fill="#8b949e">[\d,]+</tspan><tspan fill="#484f58"> \| ',
    f'</tspan><tspan fill="#c9d1d9">Commits:</tspan> <tspan fill="#484f58">..............</tspan> <tspan fill="#8b949e">{total_commits:,}</tspan><tspan fill="#484f58"> | ',
    svg_content
)

# 4. Followers
svg_content = re.sub(
    r'</tspan><tspan fill="#c9d1d9">Followers:</tspan> <tspan fill="#484f58">\.\.\.</tspan> <tspan fill="#8b949e">\d+</tspan></text>',
    f'</tspan><tspan fill="#c9d1d9">Followers:</tspan> <tspan fill="#484f58">...</tspan> <tspan fill="#8b949e">{followers}</tspan></text>',
    svg_content
)

# 5. LOC
svg_content = re.sub(
    r'</tspan><tspan fill="#c9d1d9">Lines of Code on GitHub:</tspan> <tspan fill="#484f58">\.</tspan> <tspan fill="#8b949e">[\d,]+ \( <tspan fill="#3fb950">[\d,]+\+\+</tspan><tspan fill="#8b949e">, </tspan><tspan fill="#f85149">[\d,]+--</tspan><tspan fill="#8b949e"> \)</tspan></tspan></text>',
    f'</tspan><tspan fill="#c9d1d9">Lines of Code on GitHub:</tspan> <tspan fill="#484f58">.</tspan> <tspan fill="#8b949e">{total_loc:,} ( <tspan fill="#3fb950">{total_additions:,}++</tspan><tspan fill="#8b949e">, </tspan><tspan fill="#f85149">{total_deletions:,}--</tspan><tspan fill="#8b949e"> )</tspan></tspan></text>',
    svg_content
)

with open('profile.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

# --- UPDATE README.md ---
with open('README.md', 'r', encoding='utf-8') as f:
    readme_content = f.read()

readme_content = re.sub(
    r'\. Repos: \.\.\.\. \d+ \{Contributed: \d+\} \| Stars: \.\.\.\.\.\.\.\.\.\.\.\.\. \d+',
    f'. Repos: .... {public_repos} {{Contributed: {contributed_repos}}} | Stars: ............. {total_stars}',
    readme_content
)
readme_content = re.sub(
    r'\. Commits: \.\.\.\.\.\.\.\.\.\.\.\.\.\.\.\. [\d,]+ \| Followers: \.\.\.\.\.\.\.\. \d+',
    f'. Commits: ................ {total_commits:,} | Followers: ........ {followers}',
    readme_content
)
readme_content = re.sub(
    r'\. Lines of Code on GitHub: \. [\d,]+ \( [\d,]+\+\+, [\d,]+-- \)',
    f'. Lines of Code on GitHub: . {total_loc:,} ( {total_additions:,}++, {total_deletions:,}-- )',
    readme_content
)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
