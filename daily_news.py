import os
import openai
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Settings
TOPICS = {
    '"West Seattle"': "West Seattle",
    "Delridge": "Delridge",
    '"White Center" AND "Seattle"': "White Center",
    '"Highland Park" AND "Seattle"': "Highland Park"
}
NEWSAPI_KEY = os.environ["NEWSAPI_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
TO_EMAIL = os.environ["TO_EMAIL"]
FRED_API_KEY = os.environ["FRED_API_KEY"]

openai.api_key = OPENAI_API_KEY

def fetch_articles(query):
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])

    # Post-filtering for phrase + "Seattle" logic
    phrase = None
    if '"White Center"' in query:
        phrase = "white center"
    elif '"Highland Park"' in query:
        phrase = "highland park"

    filtered = []
    for article in articles:
        content = (
            (article.get("title") or "") +
            " " +
            (article.get("description") or "") +
            " " +
            (article.get("content") or "")
        ).lower()

        if phrase:
            if phrase in content and "seattle" in content:
                filtered.append(article)
        else:
            filtered.append(article)

    return filtered[:5]

    
def get_mortgage_rate():
    fred_api_key = os.environ["FRED_API_KEY"]
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=MORTGAGE30US&api_key={fred_api_key}&file_type=json"
    response = requests.get(url)
    data = response.json()
    latest = data["observations"][-1]
    return float(latest["value"])


def summarize(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Summarize each news article in 2 concise sentences."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary error: {str(e)}"

def build_email_body_html():
    body = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.5;">
        <h2>📰 Daily News Summary</h2>
    """

    rate = get_mortgage_rate()
    body += f"<p><strong>📉 30-Year Fixed Mortgage Rate:</strong> {rate:.2f}%</p><br>"

    for query, display_name in TOPICS.items():
        body += f"<h3 style='color:#2a6ebb;'>{display_name}</h3><ul>"

        articles = fetch_articles(query)
        for article in articles:
            title = article['title']
            url = article['url']
            content = article.get('description') or article.get('content') or title
            summary = summarize(content)

            body += f"""
                <li style="margin-bottom: 12px;">
                    <p><strong><a href="{url}" target="_blank" style="text-decoration:none; color:#2a6ebb;">{title}</a></strong></p>
                    <p style="margin-top:-8px;"><em>{summary}</em></p>
                </li>
            """

        body += "</ul><hr style='margin:30px 0;'>"

    body += "</body></html>"
    return body

def send_email(subject, html_body):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = TO_EMAIL

        part = MIMEText(html_body, "html")
        msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise  # Re-raise the exception to fail the GitHub Action

def verify_secrets():
    print("Verifying environment variables are set...")
    secrets = {
        "NEWSAPI_KEY": NEWSAPI_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "EMAIL_USER": EMAIL_USER,
        "EMAIL_PASS": EMAIL_PASS,
        "TO_EMAIL": TO_EMAIL
    }
    
    for name, value in secrets.items():
        if not value:
            print(f"ERROR: {name} is not set!")
        else:
            # Only show first 4 chars for security
            masked = value[:4] + "..." if len(value) > 4 else "***"
            print(f"{name} is set: {masked}")

if __name__ == "__main__":
    verify_secrets()
    
    email_body = build_email_body_html()
    send_email("Your Daily West Seattle + Delridge + Highland Park News", email_body)
