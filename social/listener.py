"""
seoclaw social listener — monitors the web for high-signal mentions of pain
points in your niche, scores them with AI, generates reply suggestions, and
sends Discord notifications so your team can engage instantly.
Usage:
    python social/listener.py social/config_example.py [--dry-run] [--demo]
    --demo     Use built-in realistic sample posts to show the full pipeline
               (useful when live sources are rate-limited)
    --dry-run  Score posts and print suggested replies without posting to Discord
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import anthropic

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ── env ──────────────────────────────────────────────────────────────────────


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()

EXA_KEY = os.getenv("EXA_API_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)


# ── demo seed posts ───────────────────────────────────────────────────────────
# Realistic posts simulating what a live Reddit/LinkedIn monitor would surface.
# Used when --demo flag is passed or when live sources return no results.

DEMO_POSTS = [
    {
        "title": "Our fashion brand has been live for 2 years, still stuck on page 5 of Google — what am I doing wrong?",
        "snippet": (
            "We sell sustainable women's clothing, been publishing blog posts weekly for 8 months, "
            "have around 200 backlinks but our organic traffic is basically flat. Big fashion sites "
            "always outrank us. We're spending $3k/month on ads because we can't figure out SEO. "
            "Our product pages don't rank at all. Is it even possible for small fashion brands to "
            "compete organically against ASOS and H&M?"
        ),
        "url": "https://reddit.com/r/SEO/comments/demo1",
        "platform": "reddit",
        "matched_keyword": "fashion brand can't rank on Google",
    },
    {
        "title": "Hired an SEO agency 6 months ago for my boutique brand, traffic went down. Anyone else?",
        "snippet": (
            "We paid $2,500/month for an SEO agency that promised first-page rankings for our "
            "boutique fashion store. Six months in and organic traffic actually dropped 30%. "
            "They say it's a Google update. I feel like I wasted $15k. Looking for alternatives — "
            "is there any tool that actually works for small fashion/apparel ecommerce? "
            "Running on Shopify if that matters."
        ),
        "url": "https://reddit.com/r/ecommerce/comments/demo2",
        "platform": "reddit",
        "matched_keyword": "fashion brand SEO help",
    },
    {
        "title": "Content strategy for fashion brand — feeling completely lost",
        "snippet": (
            "I run a small sustainable fashion startup. Everyone says 'write good content' but I "
            "don't know what keywords to target, whether to write long-form or short posts, or how "
            "to make Google understand what we sell. We have a tight budget and no SEO expertise "
            "in-house. My competitor with a worse product ranks #1 for our main keyword. "
            "What tools or resources actually help fashion brands get found organically?"
        ),
        "url": "https://reddit.com/r/Entrepreneur/comments/demo3",
        "platform": "reddit",
        "matched_keyword": "ecommerce SEO small fashion brand",
    },
]


# ── Reddit search (OAuth) ────────────────────────────────────────────────────


def reddit_search(
    query: str, subreddits: list, days_back: int = 7, num_results: int = 10
) -> list[dict]:
    """Search Reddit using OAuth — requires REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET in .env."""
    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print(
            "  [Reddit] No credentials — add REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET to .env"
        )
        return []

    # Get access token
    auth = (client_id + ":" + client_secret).encode()
    import base64

    token_req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=b"grant_type=client_credentials",
        method="POST",
    )
    token_req.add_header("Authorization", "Basic " + base64.b64encode(auth).decode())
    token_req.add_header("User-Agent", "seoclaw-listener/1.0")
    try:
        with urllib.request.urlopen(token_req, timeout=15) as r:
            token = json.loads(r.read()).get("access_token", "")
    except Exception as e:
        print(f"  [Reddit] Token error: {e}")
        return []

    time_filter = "week" if days_back <= 7 else "month"
    results = []
    targets = subreddits if subreddits else ["all"]

    for sub in targets:
        encoded = urllib.parse.quote(query)
        if sub == "all":
            url = f"https://oauth.reddit.com/search.json?q={encoded}&sort=new&t={time_filter}&limit={num_results}"
        else:
            url = f"https://oauth.reddit.com/r/{sub}/search.json?q={encoded}&sort=new&t={time_filter}&restrict_sr=1&limit={num_results}"

        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("User-Agent", "seoclaw-listener/1.0")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                for post in data.get("data", {}).get("children", []):
                    p = post.get("data", {})
                    results.append(
                        {
                            "title": p.get("title", ""),
                            "snippet": p.get("selftext", "")[:500],
                            "url": f"https://reddit.com{p.get('permalink', '')}",
                            "score": p.get("score", 0),
                            "platform": "reddit",
                        }
                    )
        except Exception as e:
            print(f"  [Reddit] {sub}: {e}")

    return results


# ── G2 competitor review monitor ─────────────────────────────────────────────


def g2_search(competitors: list, num_results: int = 5) -> list[dict]:
    """
    Search G2 via Exa for negative reviews and complaints about competitor products.
    Surfaces people actively looking to switch — the hottest possible leads.
    """
    results = []
    for competitor in competitors:
        queries = [
            f"{competitor} review too expensive not worth it alternative",
            f"what do users dislike about {competitor}",
            f"{competitor} negative review switching to competitor",
        ]
        for query in queries[:1]:  # one query per competitor keeps it fast
            payload = json.dumps(
                {
                    "query": query,
                    "numResults": num_results,
                    "type": "neural",
                    "include_domains": ["g2.com"],
                    "contents": {"text": True},
                }
            ).encode("utf-8")

            req = urllib.request.Request(
                "https://api.exa.ai/search", data=payload, method="POST"
            )
            req.add_header("x-api-key", EXA_KEY)
            req.add_header("Content-Type", "application/json")

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
                    for r in data.get("results", []):
                        text = r.get("text", "")[:500]
                        if text:
                            results.append(
                                {
                                    "title": r.get("title", ""),
                                    "snippet": text,
                                    "url": r.get("url", ""),
                                    "platform": "g2",
                                    "matched_keyword": f"{competitor} review",
                                }
                            )
            except Exception as e:
                print(f"  [G2] {competitor}: {e}")

    return results


# ── Exa search (open web — no Reddit OAuth needed) ───────────────────────────


def exa_search(query: str, num_results: int = 10) -> list[dict]:
    """Search Exa for web content related to the query."""
    payload = json.dumps(
        {
            "query": query,
            "numResults": num_results,
            "type": "neural",
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://api.exa.ai/search", data=payload, method="POST"
    )
    req.add_header("x-api-key", EXA_KEY)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = []
            for r in data.get("results", []):
                url = r.get("url", "")
                title = r.get("title", "")
                snippet = r.get("text", r.get("snippet", r.get("extract", "")))[:500]
                # Infer platform from URL
                if "reddit.com" in url:
                    platform = "reddit"
                elif "linkedin.com" in url:
                    platform = "linkedin"
                else:
                    platform = url.split("/")[2] if "/" in url else "web"
                results.append(
                    {
                        "title": title,
                        "snippet": snippet,
                        "url": url,
                        "platform": platform,
                    }
                )
            return results
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  [Exa error] {e.code}: {body[:100]}")
        return []
    except Exception as e:
        print(f"  [Exa error] {e}")
        return []


# ── signal scoring ───────────────────────────────────────────────────────────


def score_signal(post: dict, config: dict) -> dict:
    """Claude scores the post for signal strength."""
    prompt = f"""You are a B2B sales intelligence analyst identifying sales opportunities.
Product: {config['product_name']}
Description: {config['product_description']}
Target audience: {config['target_audience']}
Pain points we solve: {', '.join(config['pain_points'])}
Post title: {post.get('title', '')}
Post content: {post.get('snippet', '')[:1000]}
Source URL: {post.get('url', '')}
Score this post (be critical — most posts are low signal):
Return ONLY valid JSON:
{{
  "signal_score": <1-10>,
  "is_relevant": <true|false>,
  "pain_point_detected": "<which specific pain point, or null>",
  "buyer_intent": "<none|low|medium|high>",
  "reasoning": "<one sentence why this is or isn't a good opportunity>",
  "urgency": "<none|low|medium|high>"
}}
Scoring:
- 8-10: Person clearly has the problem, wants a solution, fits our ICP
- 5-7: Related pain, maybe not actively looking yet
- 1-4: General topic, not a real opportunity"""

    message = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1:
        return {"signal_score": 0, "is_relevant": False, "reasoning": "parse error"}
    return json.loads(raw[start:end])


# ── reply generation ─────────────────────────────────────────────────────────


def generate_reply(post: dict, signal: dict, config: dict) -> str:
    """Generate a helpful, non-spammy reply that naturally positions the product."""
    prompt = f"""Write a reply on behalf of someone who works at {config['product_name']}.
Goal: help the person first, then naturally mention the product as a potential next step.
Rules:
- Acknowledge their specific problem
- Give 1-2 actionable tips they can use right now, even without our product
- Mention {config['product_name']} as a tool that could help further (don't oversell)
- Under 150 words, sound human
- Do NOT start with "Great question!" or "I totally understand!"
Product: {config['product_name']} — {config['product_description']}
Pain point: {signal.get('pain_point_detected', 'general SEO struggle')}
Post title: {post.get('title', '')}
Post content: {post.get('snippet', '')[:600]}
Write only the reply text:"""

    message = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ── Discord notification ──────────────────────────────────────────────────────


def send_discord(webhook_url: str, post: dict, signal: dict, reply: str, config: dict):
    """Send a rich Discord notification for a high-signal mention."""
    score = signal.get("signal_score", 0)
    intent = signal.get("buyer_intent", "unknown")
    urgency = signal.get("urgency", "unknown")
    reason = signal.get("reasoning", "")
    url = post.get("url", "")
    platform = post.get("platform", "web").capitalize()

    score_emoji = (
        ":red_circle:"
        if score >= 9
        else (":orange_circle:" if score >= 7 else ":yellow_circle:")
    )

    message = (
        f"## {score_emoji} High-Signal Mention — Score {score}/10\n\n"
        f"**Platform:** {platform}\n"
        f"**Post:** {post.get('title', 'No title')}\n"
        f"**Link:** {url}\n\n"
        f"**Why it matters:** {reason}\n"
        f"**Buyer intent:** {intent}  |  **Urgency:** {urgency}\n\n"
        f"---\n"
        f"**Suggested reply:**\n"
        f"```\n{reply}\n```\n\n"
        f"*Niche: {config['niche']} | Keyword: {post.get('matched_keyword', 'semantic match')}*"
    )

    payload = json.dumps({"content": message}).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "DiscordBot (seoclaw, 1.0)")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"    Discord notified (HTTP {resp.status})")
    except Exception as e:
        print(f"    Discord failed: {e}")


# ── main loop ────────────────────────────────────────────────────────────────


def run(config: dict, dry_run: bool = False, demo: bool = False):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", config.get("discord_webhook", ""))
    signal_threshold = config.get("signal_threshold", 7)
    days_back = config.get("days_back", 7)

    print(f"\n{'='*56}")
    print(f"  seoclaw | Social Signal Monitor")
    print(f"  Product:   {config['product_name']}")
    print(f"  Niche:     {config['niche']}")
    print(f"  Threshold: {signal_threshold}/10")
    if demo:
        print(f"  Mode:      DEMO (using sample posts)")
    elif dry_run:
        print(f"  Mode:      dry-run (no Discord posts)")
    print(f"{'='*56}\n")

    all_posts = []

    if demo:
        # Use curated demo posts for reliable demos
        all_posts = list(DEMO_POSTS)
        print(f"  Loaded {len(all_posts)} demo posts.\n")
    else:
        subreddits = config.get("subreddits", [])
        competitors = config.get("competitors", [])

        # Reddit
        if subreddits or os.getenv("REDDIT_CLIENT_ID"):
            for keyword in config["keywords"]:
                print(f'  Reddit  → "{keyword}" ...')
                results = reddit_search(
                    keyword, subreddits=subreddits, days_back=days_back
                )
                for r in results:
                    r["matched_keyword"] = keyword
                all_posts.extend(results)

        # G2 competitor reviews
        if competitors:
            print(f"  G2      → monitoring {len(competitors)} competitors ...")
            g2_results = g2_search(competitors)
            all_posts.extend(g2_results)

        # Exa web search
        for keyword in config["keywords"][:3]:  # limit to 3 keywords for speed
            print(f'  Web     → "{keyword}" ...')
            results = exa_search(keyword, num_results=5)
            for r in results:
                r["matched_keyword"] = keyword
            all_posts.extend(results)

        # Deduplicate by URL
        seen, unique = set(), []
        for p in all_posts:
            if p.get("url") not in seen:
                seen.add(p.get("url"))
                unique.append(p)
        all_posts = unique
        print(f"\n  Found {len(all_posts)} unique results. Scoring for signal...\n")

    total_scanned = 0
    total_alerted = 0

    for post in all_posts:
        total_scanned += 1
        title = post.get("title", "No title")[:65]
        print(f"  [{total_scanned}] {title}...")

        try:
            signal = score_signal(post, config)
        except Exception as e:
            print(f"      [score error] {e}")
            continue

        score = signal.get("signal_score", 0)
        print(f"      Score {score}/10 — {signal.get('reasoning', '')[:70]}")

        if score >= signal_threshold and signal.get("is_relevant"):
            print(f"      HIGH SIGNAL — generating reply...")
            reply = generate_reply(post, signal, config)

            if dry_run or not webhook_url:
                print(f"\n  {'─'*52}")
                print(f"  POST:  {post.get('url')}")
                print(f"  REPLY:\n  {reply.replace(chr(10), chr(10)+'  ')}")
                print(f"  {'─'*52}\n")
            else:
                send_discord(webhook_url, post, signal, reply, config)

            total_alerted += 1

    print(f"\n{'='*56}")
    print(f"  Done. Scanned {total_scanned} posts, {total_alerted} high-signal alerts.")
    if total_alerted > 0 and webhook_url and not dry_run:
        print(f"  Check your Discord channel for notifications.")
    elif total_alerted > 0 and not webhook_url:
        print(f"  Set DISCORD_WEBHOOK_URL in .env to post alerts to Discord.")
    print(f"{'='*56}\n")

    return {"scanned": total_scanned, "alerted": total_alerted}


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "social/config_example.py"
    dry_run = "--dry-run" in sys.argv
    demo = "--demo" in sys.argv

    import importlib.util

    spec = importlib.util.spec_from_file_location("config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = module.CONFIG

    run(config, dry_run=dry_run, demo=demo)
