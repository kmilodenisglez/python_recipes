"""
JSON Web Token (JWT) implementation with JWS signing and verification.

This package provides utilities for working with JWS (JSON Web Signature)
according to RFC-7797, with support for detached payloads and x5c header.
"""

from .utils import (
    get_x509_cert_from_pem,
    get_x509_cert_from_der,
    get_private_key_from_pem,
    sign_message_detached,
    verify_message_detached
)

__all__ = [
    'get_x509_cert_from_pem',
    'get_x509_cert_from_der',
    'get_private_key_from_pem',
    'sign_message_detached',
    'verify_message_detached'
]

def hello() -> str:
    return "Hello from json-web-token!"
