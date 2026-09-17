import os
import requests
import random
from datetime import datetime

WP_SITE = os.environ.get("WP_URL")
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")
SUBSTACK_URL = os.environ.get("SUBSTACK_URL", "https://yourname.substack.com")

if WP_SITE:
    WP_SITE = WP_SITE.replace("https://", "").replace("http://", "").strip("/")

API_URL = f"https://public-api.wordpress.com/wp/v2/sites/{WP_SITE}/posts"

TEASERS = [
    {
        "title": "The DTCC Is Tokenizing Trillions. Here's What That Actually Means.",
        "content": f"<p>The Depository Trust & Clearing Corporation — the backbone of US securities settlement — is moving to tokenize custodied assets. This isn't a crypto experiment. This is the plumbing being rebuilt.</p><p>I broke down what's actually happening, which banks benefit, and what it means for the $X trillion in daily settlement volume: <a href='{SUBSTACK_URL}'>{SUBSTACK_URL}</a></p><p>Free subscribers get weekly headlines. Paid subscribers get the full analysis plus action items.</p>"
    },
    {
        "title": "Stablecoins Are Eating Interbank Settlement. Banks Are Just Noticing.",
        "content": f"<p>Monthly stablecoin transfer volume is now comparable to major card networks. The rails are being rebuilt in real time, and most bank strategy teams haven't updated their 5-year plans.</p><p>Full breakdown of who's winning, who's losing, and the regulatory tailwinds: <a href='{SUBSTACK_URL}'>{SUBSTACK_URL}</a></p><p>Every week I translate the transformation of the financial system into a 5-minute briefing.</p>"
    },
    {
        "title": "Agentic AI Is Making Credit Decisions at Machine Speed. Compliance Isn't Ready.",
        "content": f"<p>Banks deploying agentic AI for underwriting and customer journeys are seeing measurable revenue lifts — and creating new audit trails that regulators are only beginning to understand.</p><p>What this means for your risk framework, and the 3 things to document now: <a href='{SUBSTACK_URL}'>{SUBSTACK_URL}</a></p><p>Free headlines weekly. Full analysis for paid subscribers.</p>"
    },
    {
        "title": "Open Banking Just Went Global. Here's the State of Play in 2026.",
        "content": f"<p>UK APIs are at 99% uptime, New Zealand doubled data-sharing requests in two months, Canada released draft CDB regulations. The infrastructure layer for the next decade of financial services is being laid right now.</p><p>Full country-by-country breakdown: <a href='{SUBSTACK_URL}'>{SUBSTACK_URL}</a></p>"
    }
]

def publish_teaser():
    post = random.choice(TEASERS)
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    payload = {
        "title": post["title"],
        "content": post["content"],
        "status": "publish"
    }
    r = requests.post(API_URL, auth=auth, json=payload, timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 201:
        print(f"Published: {r.json().get('link')}")
    else:
        print(f"Response: {r.text[:500]}")

if __name__ == "__main__":
    publish_teaser()