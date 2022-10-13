# Requester

The Requester defines how to prepare HTTP requests to send to the source API. The current implementation is called the HttpRequester, which is defined by:

- A base url: The root of the API source
- A path: The specific endpoint to fetch data from for a resource
- The HTTP method: the HTTP method to use (GET or POST)
- A [request options provider](request-options.md): Defines the request parameters (query parameters), headers, and request body to set on outgoing HTTP requests
- An [authenticator](authentication.md): Defines how to authenticate to the source
- An [error handler](error-handling.md): Defines how to handle errors