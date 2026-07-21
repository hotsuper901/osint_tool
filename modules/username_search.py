import concurrent.futures
from utils import http_get, save_result

PLATFORMS = {
    "GitHub":     "https://github.com/{}",
    "Twitter/X":  "https://twitter.com/{}",
    "Instagram":  "https://www.instagram.com/{}/",
    "Reddit":     "https://www.reddit.com/user/{}",
    "YouTube":    "https://www.youtube.com/@{}",
    "Telegram":   "https://t.me/{}",
    "TikTok":     "https://www.tiktok.com/@{}",
    "Pinterest":  "https://www.pinterest.com/{}/",
    "Medium":     "https://medium.com/@{}",
    "Dev.to":     "https://dev.to/{}",
    "Keybase":    "https://keybase.io/{}",
    "Twitch":     "https://www.twitch.tv/{}",
    "Steam":      "https://steamcommunity.com/id/{}",
    "Spotify":    "https://open.spotify.com/user/{}",
    "Snapchat":   "https://www.snapchat.com/add/{}",
    "Facebook":   "https://www.facebook.com/{}",
    "LinkedIn":   "https://www.linkedin.com/in/{}",
    "Xing":       "https://www.xing.com/profile/{}",
    "Behance":    "https://www.behance.net/{}",
    "Dribbble":   "https://dribbble.com/{}",
    "Flickr":     "https://www.flickr.com/people/{}",
    "Vimeo":      "https://vimeo.com/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "About.me":   "https://about.me/{}",
    "AngelList":  "https://angel.co/u/{}",
    "ProductHunt":"https://www.producthunt.com/@{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "GitLab":     "https://gitlab.com/{}",
    "Bitbucket":  "https://bitbucket.org/{}/",
    "Patreon":    "https://www.patreon.com/{}",
    "Gravatar":   "https://www.gravatar.com/{}",
    "Disqus":     "https://disqus.com/by/{}/",
    "SlideShare": "https://www.slideshare.net/{}",
    "Tumblr":     "https://{}.tumblr.com",
    "WordPress":  "https://{}.wordpress.com",
    "Kaggle":     "https://www.kaggle.com/{}",
    "Replit":     "https://replit.com/@{}",
    "CodePen":    "https://codepen.io/{}",
}

def check(platform, url_template, username):
    url = url_template.format(username)
    try:
        r = http_get(url, timeout=4)
        if r.status_code == 200:
            return (platform, url)
    except:
        pass
    return None

def run(username):
    print(f"\n{'='*60}")
    print(f"  USERNAME SEARCH (30+) - Target: {username}")
    print(f"{'='*60}")

    output = [f"Username: {username}"]
    print(f"  [i] Searching {len(PLATFORMS)} platforms...\n")

    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        fs = {ex.submit(check, p, u, username): p for p, u in PLATFORMS.items()}
        for f in concurrent.futures.as_completed(fs):
            result = f.result()
            if result:
                found.append(result)
                print(f"  [+] {result[0]:15s} -> {result[1]}")

    if found:
        print(f"\n  [i] Total found: {len(found)}/{len(PLATFORMS)}")
        output.append(f"Found ({len(found)}):")
        for p, u in sorted(found):
            output.append(f"  {p:15s} {u}")
    else:
        print("\n  [-] No profiles found")
        output.append("No profiles found")

    save_result("username", username, "\n".join(output))
