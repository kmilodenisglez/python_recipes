from __future__ import annotations

import base64
import json
import logging
from typing import Dict, Any, Optional, Union, List

import requests
from jwt import api_jws as jws
from jwt.exceptions import InvalidTokenError
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.x509 import Certificate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_x509_cert_from_pem(pem_data: bytes) -> Certificate:
    """
    Load an X.509 certificate from PEM-encoded data.
    
    Args:
        pem_data: PEM-encoded certificate data
        
    Returns:
        Certificate object
        
    Raises:
        ValueError: If certificate cannot be loaded
    """
    try:
        cert: Certificate = x509.load_pem_x509_certificate(pem_data)
    except Exception as e:
        logger.error(f"Failed to load PEM certificate: {e}")
        raise ValueError(f"Invalid PEM certificate: {e}") from e
    return cert


def get_x509_cert_from_der(der_data: bytes) -> Certificate:
    """
    Load an X.509 certificate from DER-encoded data.
    
    Args:
        der_data: DER-encoded certificate data
        
    Returns:
        Certificate object
        
    Raises:
        ValueError: If certificate cannot be loaded
    """
    try:
        cert: Certificate = x509.load_der_x509_certificate(der_data)
    except Exception as e:
        logger.error(f"Failed to load DER certificate: {e}")
        raise ValueError(f"Invalid DER certificate: {e}") from e
    return cert


def get_private_key_from_pem(pem_data: bytes, password: Optional[bytes] = None) -> RSAPrivateKey:
    """
    Load an RSA private key from PEM-encoded data.
    
    Args:
        pem_data: PEM-encoded private key data
        password: Optional password if the key is encrypted
        
    Returns:
        RSAPrivateKey object
        
    Raises:
        ValueError: If private key cannot be loaded
    """
    try:
        private_key = load_pem_private_key(pem_data, password=password)
        if not isinstance(private_key, RSAPrivateKey):
            raise ValueError("The provided key is not an RSA private key")
        return private_key
    except Exception as e:
        logger.error(f"Failed to load private key: {e}")
        raise ValueError(f"Invalid private key: {e}") from e


def _validate_headers(headers: Dict[str, Any]) -> None:
    """
    Validate JWS headers for required fields.
    
    Args:
        headers: JWS headers dictionary
        
    Raises:
        ValueError: If headers are invalid
    """
    if not headers:
        raise ValueError("Headers cannot be empty")
        
    if "b64" not in headers:
        raise ValueError("Missing 'b64' header parameter")
        
    if headers["b64"] is not False:
        raise ValueError("'b64' header parameter must be false")
        
    if "crit" not in headers:
        raise ValueError("Missing 'crit' header parameter")
        
    if "b64" not in headers["crit"]:
        raise ValueError("'b64' must be in 'crit' header parameter")
        
    if "x5c" not in headers:
        raise ValueError("Missing 'x5c' header parameter")
        
    if not isinstance(headers["x5c"], list) or not headers["x5c"]:
        raise ValueError("'x5c' header parameter must be a non-empty list")


def sign_message_detached(
        private_key: RSAPrivateKey,
        certificate_chain: bytes,
        payload_no_encoded: Dict[str, Any]
) -> str:
    """
    Sign message using PS256 alg, b64 = false and x5c header.

    Args:
        private_key: The private key used to sign a message
        certificate_chain: The decoded bytes of the X.509 certificate (DER encoded)
        payload_no_encoded: The payload (not encoded)

    Returns:
        A detached JWS token
        
    Raises:
        ValueError: If signing fails
    """
    try:
        # encode DER certificate to base64
        x5c: str = base64.standard_b64encode(certificate_chain).decode('utf-8')

        # check that detached content is automatically detected when b64 is false
        # insert x5c header
        headers = {"b64": False, "crit": ["b64"], "x5c": [x5c]}

        payload: bytes = json.dumps(payload_no_encoded, separators=(",", ":")).encode()

        return jws.encode(payload, private_key, "PS256", headers)
    except Exception as e:
        logger.error(f"Failed to sign message: {e}")
        raise ValueError(f"Failed to sign message: {e}") from e


def verify_message_detached(
        token_detached: str, 
        payload_no_encoded: Dict[str, Any],
        public_key: Optional[RSAPublicKey] = None
) -> bool:
    """
    Verify a JWS token detached using PS256, get public key from x5c header.

    The public key is obtained from the certificate in x5c header if public_key is None.

    Args:
        token_detached: The JWS Token string
        payload_no_encoded: The payload (not encoded)
        public_key: Optional public key used to verify message signature

    Returns:
        True if verification succeeds, False otherwise
    """
    try:
        if public_key is None:
            # get headers
            headers: Dict[str, Any] = jws.get_unverified_header(token_detached)
            # validate headers
            _validate_headers(headers)
            # get x5c value
            x5c_header: List[str] = headers.get('x5c')
            # decode x5c value
            certificate_chain_bytes: bytes = base64.standard_b64decode(x5c_header[0])

            # get digital certificate of x5c header attrib
            crt_der: Certificate = get_x509_cert_from_der(certificate_chain_bytes)
            # get public key from certificate DER
            public_key = crt_der.public_key()

        payload = json.dumps(payload_no_encoded, separators=(",", ":")).encode()

        jws.decode(token_detached, public_key, algorithms=['PS256'],
                   detached_payload=payload)
    except Exception as e:
        logger.debug(f"Verification failed: {e}")
        return False
    return True