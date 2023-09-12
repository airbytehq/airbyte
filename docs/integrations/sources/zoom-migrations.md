# Zoom Migration Guide

## Upgrading to 1.0.0

There was a major update to authentication for the Zoom connector. Zoom has [deprecated JWT](https://developers.zoom.us/docs/internal-apps/jwt-faq/) auth and now supports Oauth.

To migrate smoothly, use server-to-server Oauth or create an Oauth app on Zoom and delete the existing JWT application. 

It is possible to get a one-time extension up until November 10th. More details [here](https://developers.zoom.us/docs/internal-apps/jwt-faq/#:~:text=Q%3A%20My%20JWT%20app%20was%20deprecated!%20Can%20I%20get%20an%20extension%3F%20How%20do%20I%20re%2Dactivate%20it%3F)
