# OneSignal

## Overview

OneSignal is a customer messaging and engagement platform that allows businesses to create meaningful customer connections. OneSignal REST API allows a developer to retrieve audience and messaging information on the OneSignal platform.

## Endpoints

OneSignal API consists of four endpoints which can be extracted data from:

1. **App**: The collection of audience and messaging channels.
2. **Device**: A customer's device which can send message to, it is associated with app.
3. **Notification**: A messaging activity associated with app.
4. **Outcome**: Aggregated information associated with app, for example, session duration, number of clicks, etc.

## Quick Notes

- Each app has its own authentication key to retrieve its devices, notifications and outcomes. The key can be found in the app's endpoint response.

- Device and notification endpoint has 300 and 50 records limit per request respectively, so the cursor pagination strategy is used for them.

- Rate limiting follows [https://documentation.onesignal.com/docs/rate-limits](https://documentation.onesignal.com/docs/rate-limits), when a 429 HTTP status code returned.

- For the outcome endpoint, it needs to specify a comma-separated list of names and the value (sum/count) for the returned outcome data. So this requirement is added to the source spec.

## API Reference

The API reference documents: [https://documentation.onesignal.com/reference](https://documentation.onesignal.com/reference)
