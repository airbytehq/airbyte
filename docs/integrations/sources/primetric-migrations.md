# Primetric Migration Guide

## Upgrading to 1.0.0

The uuid field now have a string format (without 'format: uuid') for all streams, the destination should me managed according to that if needed.
The Assignments stream schema property financial_client_currency_exchange_rate has changed its type to string.
The Organization_rag_scopes stream has schema changes to include order and uuid.
