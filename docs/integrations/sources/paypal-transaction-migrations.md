# Paypal Transaction Migration Guide

## Upgrading to 2.1.0

Version 2.1.0 changes the format of the state object. Upgrading to 2.1.0 is safe, but downgrading to 2.0.0 is not.

To downgrade to 2.0.0:

- Edit your connection state:
  - Change the keys for the transactions and balances streams to "date"
  - Change the format of the cursor to "yyyy-MM-dd'T'HH:mm:ss+00:00"
    Alternatively, you can also reset your connection.
