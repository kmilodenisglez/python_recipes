import os
import ssl
import json
import base64
import unittest

from jwt import api_jws as jws
from jwt.utils import base64url_decode
from cryptography.x509 import Certificate
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from utils import get_x509_cert_from_pem, get_private_key_from_pem, sign_message_detached, \
    verify_message_detached

current_dir: str = os.path.dirname(__file__)
certificates_dir: str = os.path.abspath(os.path.join(current_dir, 'testcerts'))


class CertType:
    CRT = "certificate"
    PRK = "private_key"


examples_cert: dict = {}


def load_all_crypto_artifacts():
    for file in os.listdir(certificates_dir):
        if file.endswith(".pem"):
            print(file)
            with open(os.path.join(certificates_dir, file), 'rb') as cert_file:
                try:
                    cert = cert_file.read()
                    if file.endswith('priv_sk.pem'):
                        examples_cert[CertType.PRK] = cert
                    elif file.endswith('example-cert.pem'):
                        examples_cert[CertType.CRT] = cert
                except Exception as e:
                    print(e)
                    raise e


payload_no_encoded: dict = {"data": {
    "request": {
        "info_ex1": "value 1",
        "info_ex2": "value 1",
    }
}}


def sign_for_client(_payload_no_encoded: dict[str, any]):
    # get digital certificate from .pem file
    crt: bytes = examples_cert.get(CertType.CRT)
    # convert certificate from PEM to DER format
    crt_der: bytes = ssl.PEM_cert_to_DER_cert(crt.decode(encoding="utf-8"))

    # get private key from .pem file
    private_key: RSAPrivateKey = get_private_key_from_pem(examples_cert.get(CertType.PRK))

    # sign payload
    x_jws_signature_client: str = sign_message_detached(private_key, crt_der, _payload_no_encoded)

    attachments_protected, none, attachments_signature = x_jws_signature_client.split(".", maxsplit=3)

    payload = _payload_no_encoded.copy()
    payload["attachments"] = {
        "original_message": {
            "protected": attachments_protected,
            "signature": attachments_signature
        }
    }
    return payload, x_jws_signature_client


class TestSignJWSToken(unittest.TestCase):
    def setUp(self):
        # loading cryptographic artifacts
        load_all_crypto_artifacts()

    def test_sign_and_verify_payload_detached_by_client_success(self):
        payload, x_jws_signature_client = sign_for_client(payload_no_encoded)
        print("headers: ", jws.get_unverified_header(x_jws_signature_client))
        print("attachments: ", payload["attachments"])

        # VERIFY X-JWS-SIGNATURE
        assert verify_message_detached(x_jws_signature_client, payload_no_encoded) is True

    def test_sign_and_verify_payload_detached_by_sender_success(self):
        payload_to_sender, _ = sign_for_client(payload_no_encoded)

        # get digital certificate from .pem file
        crt: bytes = examples_cert.get(CertType.CRT)
        # convert certificate from PEM to DER format
        crt_der: bytes = ssl.PEM_cert_to_DER_cert(crt.decode(encoding="utf-8"))

        # get private key from .pem file
        private_key: RSAPrivateKey = get_private_key_from_pem(examples_cert.get(CertType.PRK))

        # sign message
        x_jws_signature_sender: str = sign_message_detached(private_key, crt_der, payload_to_sender)

        # VERIFY X-JWS-SIGNATURE
        verify_message_detached(x_jws_signature_sender, payload_to_sender)

        print("token: ", x_jws_signature_sender)
        print("headers: ", jws.get_unverified_header(x_jws_signature_sender))

    def test_check_headers_x_jws_signature(self):
        _, x_jws_signature_client = sign_for_client(payload_no_encoded)
        msg_header, msg_payload, _ = x_jws_signature_client.split(".")
        msg_header = base64url_decode(msg_header.encode())
        msg_header_obj = json.loads(msg_header)

        assert "b64" in msg_header_obj
        assert msg_header_obj["b64"] is False
        # Check that the payload is not inside the token
        assert not msg_payload

        # get digital certificate from .pem file
        crt: bytes = examples_cert.get(CertType.CRT)
        # convert certificate from PEM to DER format
        crt_der: bytes = ssl.PEM_cert_to_DER_cert(crt.decode(encoding="utf-8"))
        # encode DER certificate to base64
        expected: list[str] = [base64.standard_b64encode(crt_der).decode('utf-8')]

        actual: list[str] = msg_header_obj["x5c"]
        assert actual == expected

    def test_verify_x_jws_token_using_publicKey_from_pem_file_success(self):
        # get digital certificate from .pem file
        crt: Certificate = get_x509_cert_from_pem(examples_cert.get(CertType.CRT))

        # get public key from certificate
        public_key = crt.public_key()

        _, x_jws_signature_client = sign_for_client(payload_no_encoded)

        verify_message_detached(x_jws_signature_client, payload_no_encoded, public_key=public_key)


if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()
