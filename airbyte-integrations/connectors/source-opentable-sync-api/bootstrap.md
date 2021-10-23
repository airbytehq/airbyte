Opentable Sync API

Opentable is a service which allows guests to book their preferred venue for having lunhc/dinner.

Sync API is the service Opentable probides in order to programmatically pull the lastest reservations and some details about the guests willing to attend the venue.

It uses OAuth authentication with BASIC token and it consists of 2 different API Endpoints:
- Guests: providing some details related to the guests whi booked an event
- Reservations: the list of reservations made by guests in the venue(s).

In order to extract the information from the two endpoint, a Restaurant ID (RID) is needed.

More detailed info can be found at https://platform.opentable.com/documentation