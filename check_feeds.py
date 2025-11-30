import feedparser

feeds = [
    "https://feeds.transistor.fm/acquired",
    "https://api.substack.com/feed/podcast/69345.rss",
    "https://lexfridman.com/feed/podcast/",
    "https://investlikethebest.libsyn.com/rss",
    "https://feeds.megaphone.fm/investlikethebest"
]

for url in feeds:
    print(f"Checking {url}...")
    try:
        d = feedparser.parse(url)
        print(f"  Title: {d.feed.title}")
        print(f"  Entries: {len(d.entries)}")
        if d.entries:
            print(f"  Latest: {d.entries[0].title}")
            print(f"  Date: {d.entries[0].published}")
    except Exception as e:
        print(f"  Error: {e}")
    print("-" * 20)
