# Security Notes for Hugging Face Datasets Destination Connector

## Token Handling

- Hugging Face tokens are stored as secrets and never logged or exposed in error messages
- Tokens are only used for authentication with Hugging Face Hub
- Tokens are not persisted in plain text

## Security Best Practices

- Use tokens with minimal required permissions
- Rotate tokens regularly
- Never share or commit tokens to version control
