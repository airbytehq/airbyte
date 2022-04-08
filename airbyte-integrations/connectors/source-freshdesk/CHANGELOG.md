# Changelog

## 0.2.9
Maximum pagination limit `maximum_page = 500` is removed.

## 0.2.8
Include `requester` and `stats` fields in `tickets` stream

## 0.2.7
Add start_date parameter to specification from which to start pulling data.

## 0.2.6
Fix `unique_external_id` type in `contacts` schema. Should be a string 
instead of an integer.

## 0.2.4
Fix the issue when server doesn't allow the client to fetch more than 300 pages from Tickets Stream:
`Validation failed: [{'field': 'page', 'message': 'You cannot access tickets beyond the 300th page. Please provide a smaller page number.', 'code': 'invalid_value'}]`

## 0.2.3
Fix discovery and set default cursor field as "updated_at"
