import os
import openai
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Settings
TOPICS = ["West Seattle", "Delridge"]
NEWSAPI_KEY = os.environ["NEWSAPI_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
TO_EMAIL = os.environ["TO_EMAIL"]

openai.api_key = OPENAI_API_KEY

def fetch_articles(query):
    try:
        # Wrap the query in quotes to search for the exact phrase
        quoted_query = f'"{query}"'
        url = f"https://newsapi.org/v2/everything?q={quoted_query}&sortBy=publishedAt&language=en&apiKey={NEWSAPI_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json().get("articles", [])[:5]
    except Exception as e:
        print(f"Error fetching articles for {query}: {str(e)}")
        return []

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
    body = "<html><body>"
    body += "<h2>📰 Daily News Summary</h2>"

    for topic in TOPICS:
        body += f"<h3>{topic}</h3><ul>"
        articles = fetch_articles(topic)
        for article in articles:
            title = article['title']
            url = article['url']
            content = article.get('description') or article.get('content') or title
            summary = summarize(content)
            body += f"<li><a href='{url}'>{title}</a><br><small>{summary}</small></li><br>"
        body += "</ul><hr>"

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
    send_email("Your Daily West Seattle + Delridge News", email_body)
