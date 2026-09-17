import feedparser
import json
import os
import hashlib
from datetime import datetime

# --- FREE FINANCIAL SYSTEM FEEDS ---
FEEDS = {
    "a16z Crypto": "https://a16zcrypto.com/feed/",
    "BIS": "https://www.bis.org/list/bis_publications/rss.xml",
    "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ECB": "https://www.ecb.europa.eu/rss/press.html",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "The Block": "https://www.theblock.co/rss.xml",
    "Finextra": "https://www.finextra.com/rss/headlines.aspx",
    "PYMNTS": "https://www.pymnts.com/feed/",
    "IMF": "https://www.imf.org/en/News/RSS?language=eng",
    "CoinTelegraph": "https://cointelegraph.com/rss",
}

# --- RELEVANCE FILTER (transformation keywords) ---
KEYWORDS = [
    "tokenization", "tokenize", "stablecoin", "cbdc", "digital currency",
    "defi", "tradfi", "agentic ai", "open banking", "real-time payments",
    "cross-border", "programmable money", "on-chain", "settlement",
    "interoperability", "digital euro", "digital dollar", "cbdc pilot",
    "asset tokenization", "rwa", "real world assets", "blockchain",
    "distributed ledger", "dl", "smart contract", "instant payment",
    "fednow", "t+0", "t+1", "custody", "digital asset", "crypto regulation",
    "mica", "genius act", "clarity act", "payment modernization"
]

def is_relevant(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in KEYWORDS)

def make_id(title, source):
    """Create a stable hash so we can deduplicate the same story across sources."""
    return hashlib.md5(f"{source}|{title}".encode()).hexdigest()[:12]

def fetch_feed(name, url):
    """Fetch and filter entries from a single RSS feed. Fails silently on errors."""
    items = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:25]:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            link = entry.get("link", "")
            published = entry.get("published", datetime.now().isoformat())

            if is_relevant(title + " " + summary):
                items.append({
                    "id": make_id(title, name),
                    "source": name,
                    "title": title,
                    "summary": summary[:600],
                    "link": link,
                    "published": published,
                    "fetched": datetime.now().isoformat()
                })
    except Exception as e:
        print(f"[SKIP] {name}: {e}")
    return items

def deduplicate(items):
    """Remove duplicate stories (same ID) and near-duplicates (same title keywords)."""
    seen_ids = set()
    unique = []
    for item in items:
        if item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])
        unique.append(item)
    return unique

def main():
    all_items = []
    for name, url in FEEDS.items():
        items = fetch_feed(name, url)
        all_items.extend(items)
        print(f"{name}: {len(items)} relevant items")

    all_items = deduplicate(all_items)

    # Sort by fetched time (newest first)
    all_items.sort(key=lambda x: x.get("fetched", ""), reverse=True)

    # Keep top 30 for the writer (prevents context bloat)
    all_items = all_items[:30]

    with open("raw_intel.json", "w") as f:
        json.dump(all_items, f, indent=2)

    print(f"\nTotal: {len(all_items)} unique items saved to raw_intel.json")

    # Source breakdown
    from collections import Counter
    sources = Counter(i["source"] for i in all_items)
    print("Source breakdown:")
    for src, count in sources.most_common():
        print(f"  {src}: {count}")

if __name__ == "__main__":
    main()