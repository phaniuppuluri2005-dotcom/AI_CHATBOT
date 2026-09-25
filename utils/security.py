"""
Security, Input Validation, and Credential Redaction Utility.
Ensures clean, safe input handling and protects secret API keys from UI exposure.
"""

import re
import html
from typing import Tuple, List, Optional

# Max upload file size: 15 MB
MAX_UPLOAD_SIZE_BYTES = 15 * 1024 * 1024

# Allowed file extensions for document AI
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".txt", ".docx", ".md"}


def sanitize_input(text: str) -> str:
    """Sanitize user input against script injection or malicious prompt framing."""
    if not text:
        return ""
    # Strip dangerous HTML tags
    cleaned = html.escape(text.strip())
    # Remove null bytes
    cleaned = cleaned.replace('\x00', '')
    return cleaned


def redact_api_keys(text: str) -> str:
    """Redact secret keys or tokens from string outputs or stack traces."""
    if not text:
        return ""
    # Redact common API key patterns (e.g. AIzaSy..., sk-..., etc.)
    text = re.sub(r'AIzaSy[A-Za-z0-9_\-]{33}', '[REDACTED_GEMINI_KEY]', text)
    text = re.sub(r'sk-[A-Za-z0-9]{32,}', '[REDACTED_API_KEY]', text)
    text = re.sub(r'(?i)(api[_\-]?key|secret|password)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{16,}["\']?', r'\1: [REDACTED]', text)
    return text


def validate_file_upload(filename: str, size_bytes: int) -> Tuple[bool, str]:
    """Validate uploaded document files for extension and size safety."""
    if size_bytes > MAX_UPLOAD_SIZE_BYTES:
        return False, f"File size exceeds maximum limit of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB."

    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed extensions: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"

    return True, "File is valid."
