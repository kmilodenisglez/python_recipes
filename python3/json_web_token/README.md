# JWS-Signature examples

Implementation of sign/verify functions using RFC-7797 / JWS (Detached Payload) and x5c parameter attribute.

## Overview

This project demonstrates how to:
- Create and verify JWS signatures with detached payloads (RFC-7797)
- Use x5c header parameter for certificate chain validation
- Handle RSA keys and X.509 certificates

## Files

- `src/json_web_token/utils.py`: Core functions for signing and verifying JWS messages
- `src/json_web_token/__init__.py`: Package exports
- `tests/test_jws_signature.py`: Unit tests demonstrating usage
- `testcerts/`: Example certificates and private keys for testing

## Setup with Rye (Recommended)

[Rye](https://rye-up.com/) is a modern Python package manager that simplifies dependency management and virtual environment setup.

### 1. Install Rye

**On Linux/macOS:**
```bash
curl -sSf https://rye-up.com/get | bash
```

**On Windows (PowerShell):**
```powershell
irm https://rye-up.com/get.ps1 | iex
```

> After installation follow the steps shown by the rye installation

### 2. Clone and Set Up the Project

```bash
cd python3/json_web_token
rye sync
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up the project for development

### 3. Run Tests

```bash
# Run all tests
rye test
```

```bash
# Run tests with verbose output
rye test -- -v
```


## Alternative Setup (without Rye)

If you prefer not to use Rye, you can use pip:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -e .
pip install pytest

# Run tests
pytest tests/
```

## Example Usage

```python
import ssl
from json_web_token import (
    get_x509_cert_from_pem,
    get_private_key_from_pem,
    sign_message_detached,
    verify_message_detached
)

# Load certificate and private key
with open('testcerts/example-cert.pem', 'rb') as f:
    cert_pem = f.read()

with open('testcerts/example-priv_sk.pem', 'rb') as f:
    key_pem = f.read()

# Convert certificate from PEM to DER format
cert_der = ssl.PEM_cert_to_DER_cert(cert_pem.decode('utf-8'))

# Get private key
private_key = get_private_key_from_pem(key_pem)

# Payload to sign
payload = {
    "data": {
        "request": {
            "info_ex1": "value 1",
            "info_ex2": "value 2",
        }
    }
}

# Sign the payload
jws_token = sign_message_detached(private_key, cert_der, payload)

# Verify the signature
is_valid = verify_message_detached(jws_token, payload)
print(f"Signature valid: {is_valid}")
```

## Notes

- Tested on Python 3.9 - 3.12
- Example certificates are for testing only and should not be used in production
- The implementation follows RFC-7797 for detached JWS content