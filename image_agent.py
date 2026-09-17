import os
import re
import subprocess
from datetime import datetime

# --- CONFIG (change per newsletter) ---
NEWSLETTER_NAME = os.environ.get("NEWSLETTER_NAME", "COMPLIANCE PULSE")
TAGLINE = os.environ.get("TAGLINE", "Daily briefing for compliance teams")
ACCENT = "#3B82F6"      # blue accent
BG = "#0F172A"          # slate-900 background


def extract_headline(markdown_text):
    """Extract the first meaningful line as the headline."""
    lines = [l.strip() for l in markdown_text.split("\n") if l.strip()]
    if not lines:
        return "Today's Regulatory Briefing"

    first = lines[0]
    first = re.sub(r"^#+\s*", "", first)
    first = re.sub(r"^HEADLINE:?\s*", "", first, flags=re.IGNORECASE)
    first = first.strip('*_"\'').strip()

    # Cap for card readability
    if len(first) > 140:
        first = first[:137].rsplit(" ", 1)[0] + "..."
    return first


def pick_font_size(headline):
    """Return (font_px, line_height) scaled to headline length."""
    n = len(headline)
    if n <= 40:
        return 78, 1.05
    if n <= 70:
        return 62, 1.1
    if n <= 100:
        return 50, 1.15
    if n <= 130:
        return 42, 1.2
    return 36, 1.25


def escape_html(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


def build_html(headline, date_str):
    size, lh = pick_font_size(headline)
    safe = escape_html(headline)
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{
    width:1200px; height:630px; overflow:hidden;
    background:{BG};
    font-family:'DejaVu Sans', 'Helvetica', sans-serif;
    color:#FFFFFF;
  }}
  .accent {{
    position:absolute; left:0; top:0; bottom:0; width:8px;
    background:{ACCENT};
  }}
  .brand {{
    position:absolute; left:80px; top:70px;
    font-size:18px; letter-spacing:4px; font-weight:700;
    color:{ACCENT};
  }}
  .date {{
    position:absolute; right:80px; top:70px;
    font-size:16px; letter-spacing:2px;
    color:#94A3B8;
  }}
  .headline {{
    position:absolute; left:80px; right:80px; top:180px;
    font-size:{size}px; line-height:{lh};
    font-weight:800; letter-spacing:-1px;
    color:#FFFFFF;
  }}
  .rule {{
    position:absolute; left:80px; right:80px; bottom:110px;
    height:1px; background:#1E293B;
  }}
  .tagline {{
    position:absolute; left:80px; bottom:60px;
    font-size:16px; color:#64748B; letter-spacing:1px;
  }}
  .arrow {{
    position:absolute; right:80px; bottom:55px;
    font-size:24px; color:{ACCENT}; font-weight:700;
  }}
</style></head>
<body>
  <div class="accent"></div>
  <div class="brand">{escape_html(NEWSLETTER_NAME)}</div>
  <div class="date">{date_str}</div>
  <div class="headline">{safe}</div>
  <div class="rule"></div>
  <div class="tagline">{escape_html(TAGLINE)}</div>
  <div class="arrow">&#8594;</div>
</body></html>"""


def render(html_content, output_path):
    with open("temp_card.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    result = subprocess.run(
        ["wkhtmltoimage",
         "--width", "1200",
         "--height", "630",
         "--quality", "95",
         "--enable-local-file-access",
         "temp_card.html", output_path],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f"[ERROR] wkhtmltoimage: {result.stderr}")
        return False
    return True


def main():
    drafts = sorted(
        [f for f in os.listdir(".") if f.startswith("draft_") and f.endswith(".md")],
        reverse=True
    )
    if not drafts:
        print("No draft found. Run writer_agent.py first.")
        return

    draft_file = drafts[0]
    with open(draft_file, "r", encoding="utf-8") as f:
        content = f.read()

    headline = extract_headline(content)
    date_str = datetime.now().strftime("%B %d, %Y").upper()
    output_png = draft_file.replace(".md", ".png")

    print(f"Newsletter: {NEWSLETTER_NAME}")
    print(f"Headline: {headline}")
    print(f"Font size chosen: {pick_font_size(headline)[0]}px")

    html = build_html(headline, date_str)
    if render(html, output_png):
        print(f"[OK] Image saved: {output_png}")
    else:
        print("[FAIL] Image generation failed.")

    if os.path.exists("temp_card.html"):
        os.remove("temp_card.html")


if __name__ == "__main__":
    main()