# JWS-Signature examples
Implement sign/verify functions using RFC-7797 / JWS (Detached Payload) and x5c param attribute

> Note: This examples has only been tested with python versions 3.9 and 3.10

## Files

- `utils.py`: Functions for signing and verifying JWS messages.
- `test_jws_signature.py`: Example unit tests.
- `testcerts/`: Example certificates and private keys.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the tests:
   ```bash
   python test_jws_signature.py
   ```

## Notes

- Tested on Python 3.9 and 3.10.
- Example certificates are for testing only.