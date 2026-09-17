import os
import json
from groq import Groq
from datetime import datetime


def get_working_model(client):
    """Fetch available models and pick the best chat model."""
    try:
        models = client.models.list()
        available = [m.id for m in models.data]
        for preferred in ["openai/gpt-oss-120b", "qwen/qwen3.6-27b", "llama-3.1-8b-instant"]:
            if preferred in available:
                return preferred
        return available[0] if available else "llama-3.1-8b-instant"
    except Exception:
        return "openai/gpt-oss-120b"


# --- CONFIG ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SUBSTACK_URL = os.environ.get("SUBSTACK_URL", "https://yourname.substack.com")

client = Groq(api_key=GROQ_API_KEY)

PROMPT_TEMPLATE = """You are a financial systems analyst writing for fintech professionals, bank strategists, treasury teams, and institutional investors.

Today's date: {date}

Here are the developments detected in the last 24 hours:
{updates}

Write a 900-word analysis in plain English. Structure:

1. HEADLINE — specific, no hype, attention-grabbing. Reference the actual story.
2. WHAT HAPPENED — 2-3 paragraphs of factual summary. Cite the source by name (e.g., "According to the BIS...").
3. THE BIGGER PICTURE — 2-3 paragraphs connecting this to the broader transformation. Answer: Which rail is being rebuilt? Who wins? Who loses? What does this mean for the old system vs. the new one?
4. WHAT TO WATCH — 3-5 bullet points on next developments, dates, or things to monitor.

Tone: Analytical, direct, no jargon, no hype. Write for a strategy lead who has 5 minutes and needs to brief their boss tomorrow morning. Assume the reader is smart but not a crypto-native.

Do NOT include a call-to-action or subscription pitch. That goes in the separate teaser.
"""


def load_intel():
    with open("raw_intel.json", "r") as f:
        items = json.load(f)
    return items[:8]  # Top 8 stories for context


def generate_analysis(items):
    MODEL = get_working_model(client)
    print(f"Using model: {MODEL}")

    updates_text = "\n\n".join([
        f"[{i['source']}] {i['title']}\n{i['summary']}\nLink: {i['link']}"
        for i in items
    ])

    prompt = PROMPT_TEMPLATE.format(
        date=datetime.now().strftime("%B %d, %Y"),
        updates=updates_text
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1800
    )

    return response.choices[0].message.content


def save_draft(analysis):
    filename = f"draft_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w") as f:
        f.write(analysis)
    print(f"Draft saved: {filename}")
    print(f"Word count: {len(analysis.split())}")


def publish_to_substack(analysis):
    from substack import Api
    from substack.post import Post

    api = Api(
        email=os.environ.get("SUBSTACK_EMAIL"),
        password=os.environ.get("SUBSTACK_PASSWORD"),
        publication_url=SUBSTACK_URL
    )

    first_line = analysis.split("\n")[0].replace("# ", "").replace("HEADLINE:", "").strip()

    post = Post(
        title=first_line[:100],
        subtitle="The financial system is being rebuilt. Here's what changed today.",
        user_id=os.environ.get("SUBSTACK_USER_ID"),
        audience="everyone"
    )
    post.from_markdown(analysis)
    api.publish_draft(api.post_draft(post), send=True, share_automatically=False)
    print("Published to Substack")


if __name__ == "__main__":
    intel = load_intel()
    if not intel:
        print("No intel found. Run curator_agent.py first.")
    else:
        analysis = generate_analysis(intel)
        save_draft(analysis)
        # Uncomment the line below once you've tested the pipeline:
        # publish_to_substack(analysis)