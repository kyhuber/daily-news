# Daily News Email

A Python script that automatically sends daily email digests of news articles about specific neighborhoods in Seattle. The script uses the News API to fetch articles and OpenAI's GPT-4 to generate concise summaries.

## Features

- Fetches latest news articles about West Seattle and Delridge neighborhoods
- Uses GPT-4 to generate concise, two-sentence summaries of each article
- Sends a formatted HTML email with article links and summaries
- Runs automatically via GitHub Actions at 7 AM Pacific Time daily
- Can be manually triggered through GitHub Actions

## Prerequisites

- Python 3.10 or higher
- A News API key (get one at [newsapi.org](https://newsapi.org))
- An OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))
- A Gmail account (for sending emails)

## Setup

1. **Fork this repository**

2. **Set up GitHub Secrets**
   Go to your repository's Settings > Secrets and Variables > Actions and add the following secrets:
   - `NEWSAPI_KEY`: Your News API key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `EMAIL_USER`: Your Gmail address
   - `EMAIL_PASS`: Your Gmail App Password (not your regular Gmail password)
   - `TO_EMAIL`: The email address where you want to receive the news digest

   To create a Gmail App Password:
   1. Go to your Google Account settings
   2. Navigate to Security
   3. Enable 2-Step Verification if not already enabled
   4. Go to App Passwords
   5. Generate a new app password for "Mail"
   6. Use this 16-character password as your `EMAIL_PASS`

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Customization

### Changing Topics
To modify the neighborhoods or topics you want to track, edit the `TOPICS` list in `daily_news.py`:
```python
TOPICS = ["West Seattle", "Delridge"]  # Add or modify topics here
```

### Changing Schedule
To modify when the email is sent, edit the cron schedule in `.github/workflows/daily-news.yml`:
```yaml
schedule:
  - cron: '0 14 * * *'  # 7 AM Pacific Time
```

## Running Locally

1. Create a `.env` file in the project root:
   ```
   NEWSAPI_KEY=your_newsapi_key
   OPENAI_API_KEY=your_openai_key
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   TO_EMAIL=recipient@email.com
   ```

2. Run the script:
   ```bash
   python daily_news.py
   ```

## How It Works

1. The script fetches the 5 most recent articles for each topic using the News API
2. Each article is summarized using GPT-4
3. An HTML email is generated with links to the articles and their summaries
4. The email is sent using Gmail's SMTP server

## Troubleshooting

- If you're not receiving emails, check your spam folder
- Verify that all GitHub secrets are set correctly
- Make sure you're using a Gmail App Password, not your regular Gmail password
- Check the GitHub Actions logs for any error messages

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests! 