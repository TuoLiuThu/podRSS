# AI Podcast Aggregator

This tool automatically fetches daily updates from selected podcasts, generates AI summaries (with Chinese translation), and sends an email report. It is designed to run automatically using GitHub Actions.

## 🚀 How to Run on GitHub (Recommended)

You don't need a server. You can run this directly on GitHub for free.

### 1. Fork or Use this Repository
Click the **Fork** button or push this code to your own GitHub repository.

### 2. Configure Secrets
Go to your repository on GitHub:
1.  Click **Settings** tab.
2.  On the left sidebar, click **Secrets and variables** -> **Actions**.
3.  Click **New repository secret**.
4.  Add the following secrets one by one:

| Name | Value Example | Description |
|------|---------------|-------------|
| `SMTP_USER` | `your_email@gmail.com` | Your Gmail address. |
| `SMTP_PASSWORD` | `xxxx xxxx xxxx xxxx` | Your Gmail **App Password** (see below). |
| `OPENAI_API_KEY` | `sk-proj-...` | Your OpenAI API Key. |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | (Optional) Only if you use a proxy. |

**How to get a Gmail App Password:**
1.  Go to your [Google Account](https://myaccount.google.com/).
2.  Select **Security**.
3.  Under "Signing in to Google", select **2-Step Verification**.
4.  At the bottom, select **App passwords**.
5.  Generate a new app password for "Mail" / "Mac" (or Custom name). Copy the 16-character code.

### 3. Enable Workflow
1.  Go to the **Actions** tab in your repository.
2.  If you see a warning saying workflows are disabled, click to **Enable** them.
3.  Select **Daily Podcast Aggregator** on the left.
4.  You can wait for the daily run (00:00 UTC) or click **Run workflow** to test it immediately.

---

## 💻 Local Development (Optional)

If you want to run it on your own machine:

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file:
    ```env
    SMTP_USER=your_email@gmail.com
    SMTP_PASSWORD=your_app_password
    OPENAI_API_KEY=your_openai_api_key
    ```

3.  **Run**:
    ```bash
    python3 podcast_aggregator.py
    ```

## 🎙 Monitored Podcasts
- Acquired
- Dwarkesh Podcast
- Lex Fridman Podcast
- Invest Like the Best
