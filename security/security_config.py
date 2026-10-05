"""
Security configuration for OSINT TPRM
Implements rate limiting, input validation, and security headers
"""

import re
import time
from functools import wraps
from typing import Optional
import hashlib
import secrets

class SecurityManager:
    """Centralized security management"""

    def __init__(self):
        self.rate_limit_store = {}
        self.blocked_ips = set()
        self.session_tokens = {}

    # Input Validation
    @staticmethod
    def sanitize_domain(domain: str) -> Optional[str]:
        """
        Sanitize and validate domain input
        Prevents XSS, injection attacks, and invalid input
        """
        if not domain or not isinstance(domain, str):
            return None

        # Remove whitespace
        domain = domain.strip().lower()

        # Maximum length check (prevent DoS)
        if len(domain) > 253:
            return None

        # Remove dangerous characters
        domain = re.sub(r'[<>"\'\\/\x00-\x1f\x7f-\x9f]', '', domain)

        # Domain validation regex (RFC 1035)
        domain_pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$'

        if not re.match(domain_pattern, domain):
            return None

        # Block known malicious patterns
        blocked_patterns = [
            r'\.\.', r'localhost', r'127\.', r'0\.0\.0\.0',
            r'169\.254\.', r'192\.168\.', r'10\.', r'172\.1[6-9]\.',
            r'172\.2[0-9]\.', r'172\.3[0-1]\.'
        ]

        for pattern in blocked_patterns:
            if re.search(pattern, domain):
                return None

        return domain

    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """
        Sanitize text input to prevent XSS
        """
        if not text:
            return ""

        # Truncate to max length
        text = str(text)[:max_length]

        # HTML escape
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
            "/": "&#x2F;",
            "\\": "&#x5C;",
            "`": "&#96;",
            "=": "&#x3D;"
        }

        for char, escape in html_escape_table.items():
            text = text.replace(char, escape)

        return text

    # Rate Limiting
    def rate_limit(self, identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        Rate limiting implementation
        Returns True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()

        # Clean old entries
        self.rate_limit_store = {
            k: [t for t in v if current_time - t < window_seconds]
            for k, v in self.rate_limit_store.items()
            if any(current_time - t < window_seconds for t in v)
        }

        # Check rate limit
        if identifier not in self.rate_limit_store:
            self.rate_limit_store[identifier] = []

        request_times = self.rate_limit_store[identifier]

        if len(request_times) >= max_requests:
            return False

        # Record this request
        request_times.append(current_time)
        return True

    def is_blocked(self, identifier: str) -> bool:
        """Check if identifier is blocked"""
        return identifier in self.blocked_ips

    def block_identifier(self, identifier: str):
        """Block an identifier (IP, session, etc.)"""
        self.blocked_ips.add(identifier)

    # Session Management
    def generate_session_token(self) -> str:
        """Generate cryptographically secure session token"""
        return secrets.token_urlsafe(32)

    def verify_session_token(self, token: str) -> bool:
        """Verify session token"""
        return token in self.session_tokens

    @staticmethod
    def hash_data(data: str) -> str:
        """Hash sensitive data (for logging, etc.)"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

# Security Headers for HTTP responses
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none';"
    ),
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}

# CORS Configuration (restrictive)
CORS_CONFIG = {
    'allowed_origins': ['https://your-domain.com'],  # Update with actual domain
    'allowed_methods': ['GET', 'POST'],
    'allowed_headers': ['Content-Type'],
    'max_age': 3600
}

# Rate Limiting Configuration
RATE_LIMITS = {
    'assessment': {'max_requests': 10, 'window_seconds': 3600},  # 10 assessments per hour
    'api': {'max_requests': 100, 'window_seconds': 3600},  # 100 API calls per hour
    'login': {'max_requests': 5, 'window_seconds': 300}  # 5 login attempts per 5 min
}

# Input Validation Limits
VALIDATION_LIMITS = {
    'domain_max_length': 253,
    'text_max_length': 10000,
    'file_max_size': 10 * 1024 * 1024,  # 10MB
}

# Create global security manager instance
security_manager = SecurityManager()
