# SplitSnap 🧾

Snap the bill. Split the cost. Send the summary.

SplitSnap is a cheerful little receipt helper that turns a photo of a bill into a clean, fair breakdown — no calculator panic required.

## Why it’s cool
- Upload a receipt photo and let AI read the items
- Catch the subtotal, tax, tip/service charge, and total
- Split the bill evenly or by who ordered what
- Email the final breakdown straight to your inbox

## Stack
- Python
- Streamlit
- Google Gemini
- Gmail SMTP

## Run it locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your secrets in `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your_api_key"
   GMAIL_ADDRESS = "you@example.com"
   GMAIL_APP_PASSWORD = "your_app_password"
   ```
3. Launch the app:
   ```bash
   streamlit run app.py
   ```

## Best use
Clear photos of receipts work best. The app is built for quick, friendly bill splitting and instant email summaries.
