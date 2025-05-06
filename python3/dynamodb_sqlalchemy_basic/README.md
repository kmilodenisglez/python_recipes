# DynamoDB + SQLAlchemy Examples

Examples of integrating SQLAlchemy with Amazon DynamoDB using PyDynamoDB.

## Files

- `run_sqlalchemy_examples.py`: Main example script.
- `sqlalchemy_api.py`: Helper functions for CRUD operations.
- `settingsdata.json`: Example data to populate the table.

## Usage

1. Install PyDynamoDB and SQLAlchemy:
   ```bash
   pip install pydynamodb sqlalchemy
   ```
2. Run the main script:
   ```bash
   python run_sqlalchemy_examples.py
   ```

## Notes

- Requires AWS credentials if connecting to a real DynamoDB instance.
- The `settingsdata.json` file contains sample data.
