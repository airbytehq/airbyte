# Linnworks

Linnworks is an e-commerce sales channel and fulfillment integration platform.

The platform has two portals: seller and developer. First, to create API credentials, log in to the [developer portal](https://developer.linnworks.com) and create an application of type `System Integration`. Then click on provided Installation URL and proceed with an installation wizard. The wizard will show a token that you will need for authentication. The installed application will be present on your account on [seller portal](https://login.linnworks.net/).

Authentication credentials can be obtained on developer portal section Applications -> _Your application name_ -> Edit -> General. And the token, if you missed it during the install, can be obtained anytime under the section Applications -> _Your application name_ -> Installs.

Authentication flow is similar to OAuth2. The only notable difference is that the authentication endpoint returns a dynamic API server URL that is later used for subsequent requests.

For paginated results, all streams use max page size. Upstream pagination type [GenericPagedResult](https://apps.linnworks.net/Api/Class/linnworks-spa-commondata-Generic-GenericPagedResult) is implemented in class `LinnworksGenericPagedResult`. However, some endpoints use ad-hoc pagination styles, which are implemented directly in respective streams.

The API uses a standard HTTP 429 status code and `Retry-After` header for rate limiting. Its value is used for exponential backoff.

Linnworks API design is somewhat inconsistent and doesn't follow REST practice for providing uniform endpoints for every resource and collection of the resources. For example, collection endpoint sometimes returns only a part of resource attributes while specific resource endpoint returns all of them. In this case, N+1 requests are the only way to retrieve all attributes of all the resources of the same kind.

## Processed Orders

ProcessedOrders stream emits variable-length slice time intervals depending on the sync period. Too short, e.g., hourly interval severely reduces initial sync performance by issuing too many requests. On the other hand, too long, e.g., yearly, prevents the creation of state events.

The optimal slice time interval should yield the number of records equal to the max page size, i.e., 500. In such a case, the stream would emit a state event after each HTTP request, minimizing the number of requests and preventing repeated fetch of already fetched data in case of failure or scheduled syncs.

However, the slice time interval highly depends on the nature of upstream data and may substantially vary between different accounts. For example, consider one luxury items seller who sells a dozen items every week and another who sells thousands of items each day. The number of their processed orders in any time interval is several orders of magnitude apart.

Current intervals are chosen purely speculatively. Therefore, they might be inappropriate for some sellers and would need adjustment.
