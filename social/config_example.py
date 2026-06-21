"""
Social listener config -- copy this file, rename it, and fill in your details.
Then run: python social/listener.py social/my_config.py
"""

CONFIG = {
    # -- Who you are ------------------------------------------------------
    "product_name": "OpenSEO",
    "product_description": (
        "An AI-powered SEO tool built for fashion and retail brands. "
        "Finds low-competition keywords, audits existing content, and tracks "
        "rankings -- all without needing an in-house SEO team."
    ),
    "target_audience": (
        "Fashion brand founders, e-commerce managers, and digital marketers "
        "at small-to-mid-size fashion and retail companies."
    ),
    "pain_points": [
        "can't rank on Google against big fashion retailers",
        "don't know which keywords to target",
        "spending money on ads but not getting organic traffic",
        "no in-house SEO expertise",
        "content doesn't rank or drive traffic",
        "don't know why competitors rank higher",
    ],

    # -- What to search for -----------------------------------------------
    "niche": "fashion brands struggling with SEO and organic traffic",
    "keywords": [
        "fashion brand SEO help",
        "how to rank fashion website on Google",
        "fashion ecommerce organic traffic",
        "clothing brand not getting website traffic",
        "fashion brand marketing struggle",
        "sustainable fashion SEO strategy",
        "fashion startup website visibility",
        "ecommerce SEO small fashion brand",
    ],

    # -- Where to search --------------------------------------------------

    # G2 competitor monitoring -- surfaces people actively looking to switch
    # Add any competitor product names you want to monitor on G2
    "competitors": [
        "Ahrefs",
        "SEMrush",
        "Moz Pro",
        "Surfer SEO",
    ],

    # Reddit subreddits (requires REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET in .env)
    # Get credentials: reddit.com/prefs/apps -> create app -> script type
    "subreddits": [
        "SEO",
        "ecommerce",
        "smallbusiness",
        "fashionbusiness",
        "Entrepreneur",
        "startups",
        "digital_marketing",
    ],
    "days_back": 7,

    # -- Quality gate -----------------------------------------------------
    # Only alert on posts that score this or higher (1-10)
    "signal_threshold": 7,

    # -- Discord ----------------------------------------------------------
    # Set DISCORD_WEBHOOK_URL in your .env file, or paste it here
    # Get it from: Discord server -> channel settings -> Integrations -> Webhooks
    "discord_webhook": "",
}
