# flake8: noqa: E501
import os
import threading
import requests
from datetime import datetime
import streamlit as st


class TelegramLogger:
    """
    Background telemetry logger for NeuraFlow AI.
    Sends metadata to Telegram without blocking the Streamlit UI.
    """

    def __init__(self):
        # Support both Streamlit secrets and local .env
        try:
            self.bot_token = st.secrets.get(
                "TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", "")
            )
            self.chat_id = st.secrets.get(
                "TELEGRAM_CHAT_ID", os.getenv("TELEGRAM_CHAT_ID", "")
            )
        except Exception:
            self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
            self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def _is_configured(self):
        return bool(
            self.bot_token and self.chat_id and self.bot_token != "your_bot_token_here"
        )

    def _send_message_thread(self, text: str):
        if not self._is_configured():
            return

        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
        try:
            requests.post(self.api_url, json=payload, timeout=10)
        except Exception:
            # Silently fail to not disrupt the UI, but this could be logged locally if needed
            pass

    def _send_async(self, text: str):
        """Dispatches the Telegram network call to a background thread."""
        thread = threading.Thread(target=self._send_message_thread, args=(text,))
        thread.daemon = True
        thread.start()

    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log_upload(self, filename: str, size_bytes: int, pages: int):
        size_mb = size_bytes / (1024 * 1024)
        msg = (
            "🤖 <b>NeuraFlow AI</b>\n\n"
            "💾 <b>PDF Uploaded</b>\n"
            f"📄 Document: {filename}\n"
            f"📏 Size: {size_mb:.2f} MB\n"
            f"📑 Pages: {pages}\n"
            f"🕒 Timestamp: {self._get_timestamp()}"
        )
        self._send_async(msg)

    def log_query(
        self,
        document_name: str,
        question: str,
        provider: str,
        response_time: float,
        fallback_used: bool,
    ):
        fallback_str = "Yes ⚠️" if fallback_used else "No"
        msg = (
            "🤖 <b>NeuraFlow AI</b>\n\n"
            "💬 <b>User Activity Log</b>\n"
            f"📄 Document: {document_name}\n"
            f"❓ Question: {question}\n"
            f"🧠 Provider: {provider}\n"
            f"⚡ Response Time: {response_time:.2f}s\n"
            f"🔄 Fallback Used: {fallback_str}\n"
            f"🕒 Timestamp: {self._get_timestamp()}"
        )
        self._send_async(msg)

    def log_error(self, provider: str, error_msg: str):
        msg = (
            "🤖 <b>NeuraFlow AI</b>\n\n"
            "🚨 <b>Provider Error</b>\n"
            f"🧠 Provider: {provider}\n"
            f"❌ Error: {error_msg}\n"
            f"🕒 Timestamp: {self._get_timestamp()}"
        )
        self._send_async(msg)
