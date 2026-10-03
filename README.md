# SplitSnap

SplitSnap is a lightweight Streamlit app that reads a receipt or bill photo, extracts the line items and totals, and helps split the cost fairly between people.

## What it does
- Upload a receipt image
- Extract item names and prices with Gemini AI
- Check subtotal, tax, tip/service charge, and total
- Split evenly or by who ordered what
- Email the final breakdown to the user

## Tech stack
- Python
- Streamlit
- Google Gemini API
- Gmail SMTP

## Run locally
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
3. Start the app:
   ```bash
   streamlit run app.py
   ```

## Notes
- Best used with clear photos of receipts or bills.
- The app is designed for quick split calculations and email summaries.
