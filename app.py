from google import genai
from google.genai import types
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
    DEFAULT_PHOTO_PROMPT,
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


# Get Client - Gemini
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


# Create Client
gemini_client = get_gemini_client()
MODEL_NAME = "gemini-2.5-flash-lite"


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong {error}!"


def clean_email_text(text):
    # Keep line breaks (email supports them), just tidy the spacing
    if not text:
        return "No bill breakdown available."
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines)


def is_valid_email(address):
    # Simple check: something@something.something
    return "@" in address and "." in address.split("@")[-1] and " " not in address


def send_email(to_address, user_name, summary):
    try:
        body = f"Hi {user_name},\n\nHere is your bill breakdown from SplitSnap:\n\n"
        body += clean_email_text(summary)
        body += "\n\n- SplitSnap"

        message = MIMEText(body, "plain", "utf-8")
        message["Subject"] = "Your SplitSnap bill breakdown"
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_address

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(message)
        return True, "Email sent"
    except Exception as error:
        return False, str(error)


# step 1: User onboarding (username and email)
if "onboarded" not in st.session_state:
    st.title("SplitSnap 🧾")
    st.caption("Snap it. Split it. Email yourself the results.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        email_address = st.text_input(
            "Your email address",
            placeholder="you@example.com",
            help="This is the address SplitSnap will email the breakdown to",
        )
        submitted = st.form_submit_button("Lets go!")

    if submitted:
        if not name.strip() or not email_address.strip():
            st.warning("Please fill in both your name and email address!")
        elif not is_valid_email(email_address.strip()):
            st.warning("That doesn't look like a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email_address = email_address.strip()

            # Activate my ai
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()


# Create Chat interface

header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("SplitSnap 🧾")

with button_col:
    send_disabled = len(st.session_state.messages) <= 1
    if st.button("Send to Email", disabled=send_disabled, use_container_width=True):
        with st.spinner("Summarizing your bill..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
        success, info = send_email(
            st.session_state.email_address, st.session_state.name, summary
        )
        if success:
            st.success("Sent! Check your inbox ->")
        else:
            st.error(f"Couldn't send that: {info}")

st.caption(
    f"Logged in as {st.session_state.name} - updates go to {st.session_state.email_address}"
)

if not st.session_state.messages:
    add_message(
        "assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name)
    )
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    "Ask a question or attach a photo of your receipt",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))
    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(DEFAULT_PHOTO_PROMPT)

    with st.spinner("Reading the bill..."):
        answer = ask_gemini(parts)
    add_message("assistant", "text", answer)