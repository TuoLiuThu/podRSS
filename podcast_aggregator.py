import os
import feedparser
import requests
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USER)
RECIPIENT_EMAIL = "torialiuhey@gmail.com"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# Podcast Feeds
FEEDS = {
    "Acquired": "https://feeds.transistor.fm/acquired",
    "Dwarkesh Podcast": "https://api.substack.com/feed/podcast/69345.rss",
    "Lex Fridman Podcast": "https://lexfridman.com/feed/podcast/",
    "Invest Like the Best": "https://investlikethebest.libsyn.com/rss",
}

def get_yesterday_date():
    """Returns yesterday's date object."""
    return datetime.date.today() - datetime.timedelta(days=20)

def is_published_on_date(entry, target_date):
    """Checks if the entry was published on the target date."""
    try:
        # parsed_published is a struct_time
        published_time = entry.published_parsed
        published_date = datetime.date(published_time.tm_year, published_time.tm_mon, published_time.tm_mday)
        return published_date == target_date
    except Exception as e:
        print(f"Error parsing date for entry {entry.get('title', 'Unknown')}: {e}")
        return False

def summarize_and_translate(title, description):
    """
    Uses OpenAI to summarize the content and translate to Chinese.
    Returns a dictionary with translated title, chinese summary, english summary.
    """
    if not OPENAI_API_KEY:
        return {
            "title_cn": "Error: No OpenAI API Key",
            "summary_cn": "无法进行AI总结，未配置OpenAI API Key。",
            "summary_en": "AI Summary unavailable."
        }

    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

    prompt = f"""
    You are a helpful assistant for a podcast listener.
    I have a podcast episode titled "{title}".
    The description is:
    "{description}"

    Please provide:
    1. The title translated to Chinese.
    2. A concise summary of the episode content in Chinese (max 3 sentences).
    3. A concise summary of the episode content in English (max 3 sentences).

    Format the output as a JSON object with keys: "title_cn", "summary_cn", "summary_en".
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes podcast episodes in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        import json
        return json.loads(content)
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return {
            "title_cn": "Error: AI Processing Failed",
            "summary_cn": f"AI处理失败: {e}",
            "summary_en": "AI processing failed."
        }

def generate_email_content(updates, target_date):
    """Generates the HTML email content."""
    date_str = target_date.strftime("%Y-%m-%d")
    html = f"<html><body><h2>Podcast Daily Update - {date_str}</h2>"

    if not updates:
        html += "<p>No updates for yesterday.</p>"
    else:
        for podcast_name, episodes in updates.items():
            if not episodes:
                html += f"<h3>{podcast_name}</h3><p>No new episodes.</p>"
                continue

            html += f"<h3>{podcast_name}</h3>"
            for ep in episodes:
                html += f"<div style='border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;'>"
                html += f"<h4><a href='{ep['link']}'>{ep['title']}</a></h4>"
                html += f"<p><strong>中文标题:</strong> {ep['ai_data']['title_cn']}</p>"
                html += f"<p><strong>Summary (CN):</strong> {ep['ai_data']['summary_cn']}</p>"
                html += f"<p><strong>Summary (EN):</strong> {ep['ai_data']['summary_en']}</p>"
                html += f"<p><em><a href='{ep['link']}'>Listen / Original Link</a></em></p>"
                html += "</div>"

    html += "</body></html>"
    return html

def send_email(subject, html_content):
    """Sends the email."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("SMTP configuration missing. Printing email content instead.")
        print("Subject:", subject)
        # print("Content:", html_content) # Too verbose for logs usually
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    print("Starting Podcast Aggregator...")
    yesterday = get_yesterday_date()
    print(f"Target Date: {yesterday}")

    updates = {}

    for name, url in FEEDS.items():
        print(f"Fetching {name}...")
        try:
            feed = feedparser.parse(url)
            podcast_updates = []

            for entry in feed.entries:
                if is_published_on_date(entry, yesterday):
                    print(f"  Found new episode: {entry.title}")

                    # Clean description (remove html tags if needed, but for now pass as is)
                    description = entry.get('summary', '') or entry.get('description', '')

                    # AI Processing
                    print("  Processing with AI...")
                    ai_data = summarize_and_translate(entry.title, description)

                    podcast_updates.append({
                        "title": entry.title,
                        "link": entry.link,
                        "description": description,
                        "ai_data": ai_data
                    })

            if not podcast_updates:
                print("  No updates for this date.")
                # We still add it to updates to show "No updates" if that's desired,
                # or we can just omit it. The prompt says "If no update, state it in the daily report".
                updates[name] = []
            else:
                updates[name] = podcast_updates

        except Exception as e:
            print(f"Error fetching {name}: {e}")
            updates[name] = [] # Mark as empty or maybe error state

    # Check if there are any updates at all or if we should send a "No updates" email
    # The prompt says "give title... if no update... state it".
    # So we always send an email.

    print("Generating report...")
    html_content = generate_email_content(updates, yesterday)

    print("Sending email...")
    send_email(f"Podcast Daily Update - {yesterday}", html_content)
    print("Done.")

if __name__ == "__main__":
    main()
