import os
import openai
import requests
import smtplib
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
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    return response.json().get("articles", [])[:5]

def summarize(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Summarize each news article in 2 concise sentences."},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Summary error: {str(e)}"

def build_email_body():
    body = ""
    for topic in TOPICS:
        body += f"\n---\n**{topic}**\n"
        articles = fetch_articles(topic)
        for article in articles:
            title = article['title']
            url = article['url']
            content = article.get('description') or article.get('content') or title
            summary = summarize(content)
            body += f"\n• [{title}]({url})\n{summary}\n"
    return body

def send_email(subject, body):
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())

if __name__ == "__main__":
    email_body = build_email_body()
    send_email("Your Daily West Seattle + Delridge News Summary", email_body)
