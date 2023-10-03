# Shopify Migration Guide

## Upgrading to 1.0.0
This version uses Shopify API version `2023-07` which brings changes to the following streams:
 - removed `gateway, payment_details, processing_method` properties from `Order` stream, they are no longer supplied.
 - added `company, confirmation_number, current_total_additional_fees_set, original_total_additional_fees_set, tax_exempt, po_number` properties to `Orders` stream
 - added `total_unsettled_set, payment_id` to `Transactions` stream
 - added `return` property to `Order Refund` stream
 - added `created_at, updated_at` to `Fulfillment Order` stream

### Action items required for 1.0.0
 * The `reset` and `full-refresh` for `Orders` stream is required after upgrading to this version.
