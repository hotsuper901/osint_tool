import json
from utils import http_get, save_result

SOCIAL_PLATFORMS = {
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
    "Mastodon":   "https://mastodon.social/@{}",
    "Patreon":    "https://www.patreon.com/{}",
    "Gravatar":   "https://www.gravatar.com/{}",
    "Disqus":     "https://disqus.com/by/{}/",
    "SlideShare": "https://www.slideshare.net/{}",
    "Scribd":     "https://www.scribd.com/{}",
    "Tumblr":     "https://{}.tumblr.com",
    "WordPress":  "https://{}.wordpress.com",
    "Kaggle":     "https://www.kaggle.com/{}",
    "Replit":     "https://replit.com/@{}",
    "CodePen":    "https://codepen.io/{}",
}

def check_profile(username, platform, url_template):
    url = url_template.format(username)
    try:
        r = http_get(url, timeout=4)
        if r.status_code == 200:
            return (platform, url, r.status_code)
    except:
        pass
    return None

def run(username):
    print(f"\n{'='*60}")
    print(f"  SOCIAL MEDIA PROFILER - Target: {username}")
    print(f"{'='*60}")

    if not username:
        print("  [!] No username provided")
        return

    output = [f"Username: {username}"]

    print(f"\n  [i] Checking {len(SOCIAL_PLATFORMS)} platforms...")
    print(f"  [i] This may take a minute\n")

    found = []
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        fs = {ex.submit(check_profile, username, p, u): p for p, u in SOCIAL_PLATFORMS.items()}
        for f in concurrent.futures.as_completed(fs):
            result = f.result()
            if result:
                found.append(result)
                print(f"  [+] {result[0]:15s} -> {result[1]}")

    if not found:
        print("\n  [-] No profiles found for this username")
        output.append("No profiles found")
    else:
        print(f"\n  [i] Total: {len(found)}/{len(SOCIAL_PLATFORMS)} profiles found")
        output.append(f"Profiles found ({len(found)}):")
        for platform, url, status in sorted(found):
            output.append(f"  {platform:15s} {url}")

    save_result("social", username, "\n".join(output))
