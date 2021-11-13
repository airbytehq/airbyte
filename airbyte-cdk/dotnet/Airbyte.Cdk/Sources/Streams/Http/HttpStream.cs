using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Channels;
using System.Threading.Tasks;
using Airbyte.Cdk.Models;
using Airbyte.Cdk.Sources.Streams.Http.Auth;
using Flurl;
using Flurl.Http;
using Polly;
using Polly.Retry;
using Type = Airbyte.Cdk.Models.Type;

namespace Airbyte.Cdk.Sources.Streams.Http
{
    /// <summary>
    /// Base abstract class for an Airbyte Stream using the HTTP protocol. Basic building block for users building an Airbyte source for a HTTP API.
    /// </summary>
    public abstract class HttpStream : Stream
    {
        /// <summary>
        /// Get the latest response from the api stream
        /// </summary>
        protected IFlurlResponse LastFlurlResponse { get; private set; }

        /// <summary>
        /// Currently used sync mode
        /// </summary>
        protected SyncMode SyncMode { get; private set; }

        /// <summary>
        /// Most HTTP streams use a source defined cursor (i.e: the user can't configure it like on a SQL table)
        /// </summary>
        public virtual bool SourceDefinedCursor { get; protected set; } = true;

        /// <summary>
        /// Use this variable to define page size for API http requests with pagination support
        /// </summary>
        public virtual int? PageSize { get; set; } = null;

        private AuthBase AuthImplementation { get; set; } = null;

        /// <summary>
        /// Set the authentication implementation for this stream
        /// </summary>
        /// <param name="auth"></param>
        public void WithAuth(AuthBase auth) => AuthImplementation = auth;

        /// <summary>
        /// URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"
        /// </summary>
        /// <returns></returns>
        public abstract string UrlBase();

        /// <summary>
        /// Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        /// </summary>
        public virtual HttpMethod HttpMethod => HttpMethod.Get;

        /// <summary>
        /// Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        /// </summary>
        public virtual bool RaiseOnHttpErrors => true;

        /// <summary>
        /// Override if needed. Specifies maximum amount of retries for backoff policy. Return 0 for no limit.
        /// </summary>
        public virtual int MaxRetries => 5;

        /// <summary>
        /// Override if needed. Specifies timeout period for a request.
        /// </summary>
        public virtual TimeSpan TimeOut => TimeSpan.FromMinutes(15);

        /// <summary>
        /// Override this method to define a pagination strategy.
        /// The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.
        /// </summary>
        /// <param name="response"></param>
        /// <returns>The token for the next page from the input response object. Returning None means there are no more pages to read in this response.</returns>
        public abstract Dictionary<string, object> NextPageToken(IFlurlRequest request, IFlurlResponse response);

        /// <summary>
        /// Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        /// Defaults to {UrlBase}/{Name} where Name is the name of this stream
        /// </summary>
        /// <param name="streamstate"></param>
        /// <param name="streamslice"></param>
        /// <param name="nextpagetoken"></param>
        /// <returns></returns>
        public virtual string Path(JsonDocument streamstate = null, Dictionary<string, object> streamslice = null,
            Dictionary<string, object> nextpagetoken = null) => Name.ToLower();

        /// <summary>
        /// Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.
        /// E.g: you might want to define query parameters for paging if next_page_token is not None.
        /// </summary>
        /// <param name="streamstate"></param>
        /// <param name="streamslice"></param>
        /// <param name="nextpagetoken"></param>
        /// <returns></returns>
        public virtual Dictionary<string, object> RequestParams(JsonDocument streamstate,
            Dictionary<string, object> streamslice = null,
            Dictionary<string, object> nextpagetoken = null) => new();

        /// <summary>
        /// Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        /// </summary>
        /// <param name="streamstate"></param>
        /// <param name="streamslice"></param>
        /// <param name="nextpagetoken"></param>
        /// <returns></returns>
        public virtual Dictionary<string, object> RequestHeaders(JsonDocument streamstate,
            Dictionary<string, object> streamslice = null,
            Dictionary<string, object> nextpagetoken = null) => new();

        /// <summary>
        /// Override when creating POST/PUT/PATCH requests to populate the body of the request with a non-JSON payload.
        /// 
        /// If returns a ready text that it will be sent as is.
        /// If returns a dict that it will be converted to a urlencoded form.
        /// E.g. {"key1": "value1", "key2": "value2"} =&gt; "key1=value1&amp;key2=value2"
        /// 
        /// At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        /// </summary>
        /// <param name="streamstate"></param>
        /// <param name="streamslice"></param>
        /// <param name="nextpagetoken"></param>
        /// <returns></returns>
        public virtual string RequestBodyData(JsonDocument streamstate,
            Dictionary<string, object> streamslice = null,
            Dictionary<string, object> nextpagetoken = null) => string.Empty;

        /// <summary>
        /// Override when creating POST/PUT/PATCH requests to populate the body of the request with a JSON payload.
        /// At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        /// </summary>
        /// <param name="streamstate"></param>
        /// <param name="streamslice"></param>
        /// <param name="nextpagetoken"></param>
        /// <returns></returns>
        public virtual string RequestBodyJson(JsonDocument streamstate,
            Dictionary<string, object> streamslice = null,
            Dictionary<string, object> nextpagetoken = null) => string.Empty;

        /// <summary>
        /// Parses the raw response object into a list of records.
        /// By default, this returns an iterable containing the input. Override to parse differently.
        /// </summary>
        /// <param name="response"></param>
        /// <param name="streamstate"></param>
        /// <param name="streamslice"></param>
        /// <param name="nextpagetoken"></param>
        /// <returns></returns>
        public abstract IEnumerable<JsonDocument> ParseResponse(IFlurlResponse response, JsonDocument streamstate,
            Dictionary<string, object> streamslice = null,
            Dictionary<string, object> nextpagetoken = null);

        /// <summary>
        /// Override to set different conditions for backoff based on the response from the server.
        /// 
        /// By default, back off on the following HTTP response statuses:
        /// - 429 (Too Many Requests) indicating rate limiting
        /// - 500s to handle transient server errors
        /// 
        /// Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        /// </summary>
        /// <param name="exc"></param>
        /// <returns></returns>
        public virtual bool ShouldRetry(FlurlHttpException exc) => exc.StatusCode is 429 or 500 or < 600;

        /// <summary>
        /// Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.
        /// This method is called only if ShouldBackoff returns True for the input request.
        /// </summary>
        /// <param name="exc"></param>
        /// <returns>how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff to the default backoff behavior (e.g using an exponential algorithm).</returns>
        public virtual TimeSpan BackoffTime(int retryCount, IFlurlResponse response)
            => response.Headers.TryGetFirst("X-Retry-After", out string retryafter) ?
                TimeSpan.FromSeconds(double.TryParse(retryafter, out var result) ? result : 5) :
                TimeSpan.FromSeconds(5) * retryCount;

        public async Task<(IFlurlRequest, IFlurlResponse)> Send(string path, Dictionary<string, object> headers = null, Dictionary<string, object> parameters = null, string json = "", string data = "")
        {
            //Create initial request object
            Url requestUrl = UrlBase().AppendPathSegment(path);
            IFlurlRequest request = requestUrl.ConfigureRequest(x => x.Timeout = TimeOut);
            LastFlurlResponse = null;

            //Set header or query params
            if (headers?.Count > 0)
                request = headers.Aggregate(request, (current, header) => current.WithHeader(header.Key, header.Value));
            if (parameters?.Count > 0)
                request = parameters.Aggregate(request, (current, @params) => current.SetQueryParam(@params.Key, @params.Value));

            //Set content
            if (!string.IsNullOrWhiteSpace(json) && !string.IsNullOrWhiteSpace(data))
                throw new Exception(
                    "At the same time only one of the 'RequestBodyData' and 'RequestBodyJson' functions can return data");
            string stringContent = !string.IsNullOrWhiteSpace(json) ? json :
                !string.IsNullOrWhiteSpace(data) ? data : string.Empty;

            //Check for authentication
            switch (AuthImplementation)
            {
                case BasicAuth basicAuth:
                    request.WithBasicAuth(basicAuth);
                    break;
                case OAuth oAuth:
                    request.WithOauth(oAuth);
                    break;
            }

            //Prepare requests
            Func<Task<IFlurlResponse>> requestFunc =
                new[] { HttpMethod.Put, HttpMethod.Patch, HttpMethod.Post }.Contains(HttpMethod) ?
                    !string.IsNullOrWhiteSpace(stringContent) ? async () => await request.SendAsync(HttpMethod, new StringContent(stringContent)) :
                    async () => await request.SendAsync(HttpMethod) :
                    async () => await request.GetAsync();

            //Execute request
            try
            {
                return await GetRetryPolicy().ExecuteAsync(async () =>
                {
                    LastFlurlResponse = await requestFunc();
                    return (request, LastFlurlResponse);
                });
            }
            catch (Exception e)
            {
                if (RaiseOnHttpErrors)
                {
                    if (e is FlurlHttpException flurlHttpException)
                        Logger.Info($"Giving up for returned HTTP status: {flurlHttpException.StatusCode}");
                    throw;
                }
            }

            return (null, null);
        }

        /// <summary>
        /// Creates the retry policy to retry when needed
        /// </summary>
        /// <returns></returns>
        private AsyncRetryPolicy GetRetryPolicy() => Policy.Handle<FlurlHttpException>(ShouldRetry)
            .WaitAndRetryAsync(MaxRetries, retryCount => BackoffTime(retryCount, LastFlurlResponse),
                (exc, span, count, _) =>
                {
                    Logger.Info($"Caught retryable error '{exc.Message}' after {count} tries. Waiting {Math.Round(span.TotalSeconds)} seconds then retrying...");
                });

        /// <summary>
        /// Start reading records
        /// </summary>
        /// <param name="syncMode"></param>
        /// <param name="streamchannel"></param>
        /// <param name="recordlimit"></param>
        /// <param name="cursorfield"></param>
        /// <param name="streamslice"></param>
        /// <param name="streamstate"></param>
        /// <returns></returns>
        public override async Task<long> ReadRecords(AirbyteLogger logger, SyncMode syncMode, ChannelWriter<AirbyteMessage> streamchannel,
            long? recordlimit = null, string[] cursorfield = null,
            Dictionary<string, object> streamslice = null, JsonDocument streamstate = null)
        {
            SyncMode = syncMode;
            Logger = logger;
            bool paginationcompleted = false;
            streamstate ??= JsonDocument.Parse("{}");
            Dictionary<string, object> nextpagetoken = null;
            long recordcount = 0;
            bool Limitreached() => recordlimit.HasValue && recordcount >= recordlimit.Value;
            async Task UpdateState(JsonDocument lastrecord)
            {
                var updatedstate = GetUpdatedState(streamstate, lastrecord);
                Logger.Info($"Setting state of {Name} stream to {updatedstate.RootElement.GetRawText()}");
                await streamchannel.WriteAsync(new AirbyteMessage
                {
                    Type = Type.STATE,
                    State = new AirbyteStateMessage
                    {
                        Data = updatedstate
                    }
                });
                streamstate = updatedstate;
            }

            while (!paginationcompleted)
            {
                var requestheaders = RequestHeaders(streamstate, streamslice, nextpagetoken);
                var path = Path(streamstate, streamslice, nextpagetoken);
                var parameters = RequestParams(streamstate, streamslice, nextpagetoken);
                var requestjson = RequestBodyJson(streamstate, streamslice, nextpagetoken);
                var requestBodyData = RequestBodyData(streamstate, streamslice, nextpagetoken);
                (IFlurlRequest request, IFlurlResponse response) result = await Send(path, requestheaders, parameters, requestjson, requestBodyData);
                JsonDocument _lastitem = null;

                foreach (var item in ParseResponse(result.response, streamstate, streamslice, nextpagetoken))
                {
                    await streamchannel.WriteAsync(AbstractSource.AsAirbyteMessage(Name, item));
                    recordcount++;

                    //Check record limit
                    if (Limitreached())
                        break;

                    //Check state checkpoint
                    if (SyncMode == SyncMode.incremental && StateCheckpointInterval.HasValue &&
                        recordcount % StateCheckpointInterval == 0)
                        await UpdateState(item);

                    _lastitem = item;
                }

                nextpagetoken = NextPageToken(result.request, result.response);
                paginationcompleted = (nextpagetoken == null || nextpagetoken.Count == 0) || Limitreached();
                if (paginationcompleted && SyncMode == SyncMode.incremental)
                    await UpdateState(_lastitem);
            }

            return recordcount;
        }
    }
}
