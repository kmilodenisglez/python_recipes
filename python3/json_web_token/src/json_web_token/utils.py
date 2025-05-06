from __future__ import annotations

import base64
import json

import requests
from jwt import api_jws as jws
from jwt.exceptions import InvalidTokenError
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.x509 import Certificate


def get_x509_cert_from_pem(pem_data: bytes) -> Certificate:
    try:
        cert: Certificate = x509.load_pem_x509_certificate(pem_data)
    except Exception as e:
        raise e
    return cert


def get_x509_cert_from_der(pem_data: bytes) -> Certificate:
    try:
        cert: Certificate = x509.load_der_x509_certificate(pem_data)
    except Exception as e:
        raise e
    return cert


def get_private_key_from_pem(pem_data: bytes) -> RSAPrivateKey:
    try:
        key: RSAPrivateKey = load_pem_private_key(pem_data, password=None)
    except Exception as e:
        raise e
    return key


def sign_message_detached(
        private_key: RSAPrivateKey,
        certificate_chain: bytes,
        payload_no_encoded: dict[str, any]
) -> str:
    """
    The function sign message using PS256 alg, b64 = false and x5c header.

    :param RSAPrivateKey private_key: The private key used to sign a message.
    :param bytes certificate_chain: The decoded bytes of the X.509 certificate. Typically, a DER encoded ASN.1 structure.
    :param dict payload_no_encoded: The payload no encoded.

    :return: A token jws detached
    """
    # encode DER certificate to base64
    x5c: str = base64.standard_b64encode(certificate_chain).decode('utf-8')

    # check that detached content is automatically detected when b64 is false
    # insert x5c header
    headers = {"b64": False, "crit": ["b64"], "x5c": [x5c]}

    payload: bytes = json.dumps(payload_no_encoded, separators=(",", ":")).encode()

    return jws.encode(payload, private_key, "PS256", headers)


def verify_message_detached(token_detached: str, payload_no_encoded: dict[str, any],
                            public_key: RSAPublicKey | None = None) -> bool:
    """
    The function verify a JWS token detached using PS256, get public key from x5c header.

    The public key is obtained from the certificate in x5c header if the **public_key = None**.

    :param str token_detached: The JWS Token string.
    :param dict payload_no_encoded: The payload no encoded.
    :param RSAPublicKey public_key: The public key used to verify message (signature).
    :type public_key: RSAPublicKey, optional

    :return:
        A token jws detached
    """
    try:
        if public_key is None:
            # get headers
            headers: dict = jws.get_unverified_header(token_detached)
            # validate headers
            _validate_headers(headers)
            # get x5c value
            x5c_header: list = headers.get('x5c')
            # decode x5c value
            certificate_chain_bytes: bytes = base64.standard_b64decode(x5c_header[0])

            # get digital certificate of x5c header attrib
            crt_der: Certificate = get_x509_cert_from_der(certificate_chain_bytes)
            # get public key from certificate DER
            public_key = crt_der.public_key()

        payload = json.dumps(payload_no_encoded, separators=(",", ":")).encode()

        jws.decode(token_detached, public_key, algorithms=['PS256'],
                   detached_payload=payload)
    except Exception:
        return False
    return True


def _validate_headers(headers: dict[str, any]) -> None:
    if "x5c" in headers:
        _validate_x5c(headers["x5c"][0])
    else:
        raise InvalidTokenError("x5c header parameter required")


def _validate_x5c(x5c: str) -> None:
    if not isinstance(x5c, str):
        raise InvalidTokenError("x5c header parameter must be a string")
