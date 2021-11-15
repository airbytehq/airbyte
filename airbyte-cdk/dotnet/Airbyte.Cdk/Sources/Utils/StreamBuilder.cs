using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Channels;
using System.Threading.Tasks;
using Airbyte.Cdk.Models;
using Airbyte.Cdk.Sources.Streams.Http;
using Airbyte.Cdk.Sources.Streams.Http.Auth;
using Flurl.Http;
using Json.Schema;
using JsonCons.JsonPath;

namespace Airbyte.Cdk.Sources.Utils
{
    public static class FluenStreamBuilderExtension
    {
        public static FluentStreamBuilder HttpStream(this string baseUrl) =>
            new FluentStreamBuilder().UrlBase(() => baseUrl);
    }

    public class FluentStreamBuilder
    {
        public string Name { get; }

        private readonly IEnumerable<DynamicMethod> _methods = new List<DynamicMethod>();

        private readonly IEnumerable<DynamicProperty> _properties = new List<DynamicProperty>();

        private readonly AuthBase _authentication;

        public FluentStreamBuilder()
        {
        }

        private FluentStreamBuilder(string name, IEnumerable<DynamicMethod> methods,
            IEnumerable<DynamicProperty> properties, AuthBase authentication = null)
        {
            Name = name;
            _methods = methods;
            _properties = properties;
            _authentication = authentication;
        }


        /// <summary>
        /// Override to set different conditions for backoff based on the response from the server.
        /// 
        /// By default, back off on the following HTTP response statuses:
        /// - 429 (Too Many Requests) indicating rate limiting
        /// - 500s to handle transient server errors
        /// 
        /// Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        /// </summary>
        /// <param name="func">Input: FlurlHttpException exception | Output: boolean to retry yes or no</param>
        /// <returns></returns>
        public FluentStreamBuilder ShouldRetry(Func<FlurlHttpException, bool> func) =>
            AddFunc(func, nameof(ShouldRetry));

        /// <summary>
        /// Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.
        /// This method is called only if ShouldBackoff returns True for the input request.
        /// </summary>
        /// <param name="func">Input: int retrycount, IFlurlResponse response | Output: Timespan to backoff</param>
        /// <returns></returns>
        public FluentStreamBuilder BackoffTime(Func<int, IFlurlResponse, TimeSpan> func) =>
            AddFunc(func, nameof(BackoffTime));

        /// <summary>
        /// Override this method to define a pagination strategy.
        /// The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.
        /// </summary>
        /// <param name="func">Input: IFlurlRequest request, IFlurlResponse response | Dictionary<string, object> with next page token</param>
        /// <returns>The token for the next page from the input response object. Returning None means there are no more pages to read in this response.</returns>
        public FluentStreamBuilder NextPageToken(Func<IFlurlRequest, IFlurlResponse, Dictionary<string, object>> func) =>
            AddFunc(func, nameof(NextPageToken));

        /// <summary>
        /// Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        /// Defaults to {UrlBase}/{Name} where Name is the name of this stream
        /// </summary>
        /// <param name="func">Input: JsonElement StreamState, Dictionary<string, object> StreamSlice, Dictionary<string, object> nextpagetoken | Output string subpath for the request</param>
        /// <returns></returns>
        public FluentStreamBuilder Path(Func<JsonElement, Dictionary<string, object>?,
            Dictionary<string, object>?, string> func) =>
            AddFunc(func, nameof(Path));

        /// <summary>
        /// Parses the raw response object into a list of records.
        /// By default, this returns an iterable containing the input. Override to parse differently.
        /// </summary>
        /// <param name="func">Input: IFlurlResponse response to parse, JsonElement streamstate, Dictionary<string, object> streamslice, Dictionary<string, object> nextpagetoken | Output IEnumerable<JsonElement> records</param>
        public FluentStreamBuilder ParseResponse(
            Func<IFlurlResponse, JsonElement, Dictionary<string, object>?,
                Dictionary<string, object>?, IEnumerable<JsonElement>> func) =>
            AddFunc(func, nameof(ParseResponse));

        /// <summary>
        /// The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        /// Override as needed.
        /// </summary>
        /// <returns>A JsonSchema object representing this stream</returns>
        /// <param name="func">Input: None | Output: JsonSchema</param>
        public FluentStreamBuilder GetJsonSchema(Func<JsonSchema> func) =>
            AddFunc(func, nameof(GetJsonSchema));


        /// <summary>
        /// Override to extract state from the latest record.Needed to implement incremental sync.
        ///
        ///     Inspects the latest record extracted from the data source and the current state object and return an updated state object.
        ///
        /// For example: if the state object is based on created_at timestamp, and the current state is { 'created_at': 10}, and the latest_record is
        /// {'name': 'octavia', 'created_at': 20 } then this method would return {'created_at': 20}
        /// to indicate state should be updated to this object.
        /// </summary>
        /// <param name="func">Input: JsonElement currentstreamstate, JsonElement latestrecord | Output: JsonElement</param>
        /// <returns></returns>
        public FluentStreamBuilder GetUpdatedState(
            Func<JsonElement, JsonElement, JsonElement> func) =>
            AddFunc(func, nameof(GetUpdatedState));

        /// <summary>
        /// This method should be overridden by subclasses to read records based on the inputs
        /// </summary>
        /// <param name="func">Input: SyncMode syncmode, ChannelWriter<AirbyteMessage> streamchannel, long? recordlimit, Dictionary<string, object[]> cursorfield, Dictionary<string, object> streamslice, JsonElement streamstate | Output Task<long></long></param>
        /// <returns></returns>
        public FluentStreamBuilder ReadRecords(
            Func<AirbyteLogger, SyncMode, ChannelWriter<AirbyteMessage>, long?, string[],
                Dictionary<string, object>, Dictionary<string, object>, Task<long>> func) =>
            AddFunc(func, nameof(ReadRecords));

        /// <summary>
        /// Override when creating POST/PUT/PATCH requests to populate the body of the request with a non-JSON payload.
        /// 
        /// If returns a ready text that it will be sent as is.
        /// If returns a dict that it will be converted to a urlencoded form.
        /// E.g. {"key1": "value1", "key2": "value2"} =&gt; "key1=value1&amp;key2=value2"
        /// 
        /// At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        /// </summary>
        /// <param name="func">Input: JsonElement streamstate, Dictionary<string, object> streamslice, Dictionary<string, object> nextpagetoken | Output: string</param>
        /// <returns></returns>
        public FluentStreamBuilder RequestBodyData(
            Func<JsonElement, Dictionary<string, object>, Dictionary<string, object>, string> func) =>
            AddFunc(func, nameof(RequestBodyData));

        /// <summary>
        /// Override when creating POST/PUT/PATCH requests to populate the body of the request with a JSON payload.
        /// At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        /// </summary>
        /// <param name="func">Input: JsonElement streamstate, Dictionary<string, object> streamslice, Dictionary<string, object> nextpagetoken | Output: string</param>
        /// <returns></returns>
        public FluentStreamBuilder RequestBodyJson(
            Func<JsonElement, Dictionary<string, object>, Dictionary<string, object>, string> func) =>
            AddFunc(func, nameof(RequestBodyJson));

        /// <summary>
        /// Override when creating POST/PUT/PATCH requests to populate the body of the request with a JSON payload.
        /// At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        /// </summary>
        /// <param name="func">Input: JsonElement streamstate, Dictionary<string, object> streamslice, Dictionary<string, object> nextpagetoken | Output: Dictionary<string, object></param>
        /// <returns></returns>
        public FluentStreamBuilder RequestHeaders(
            Func<JsonElement, Dictionary<string, object>, Dictionary<string, object>,
                Dictionary<string, object>> func) =>
            AddFunc(func, nameof(RequestHeaders));

        /// <summary>
        /// Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.
        /// E.g: you might want to define query parameters for paging if next_page_token is not None.
        /// </summary>
        /// <param name="func">Input: JsonElement streamstate, Dictionary<string, object> streamslice, Dictionary<string, object> nextpagetoken | Output: Dictionary<string, object></param>
        /// <returns></returns>
        public FluentStreamBuilder RequestParams(
            Func<JsonElement, Dictionary<string, object>, Dictionary<string, object>,
                Dictionary<string, object>> func) =>
            AddFunc(func, nameof(RequestParams));

        /// <summary>
        /// Override to define the slices for this stream. See the stream slicing section of the docs for more information.
        /// </summary>
        /// <param name="func">Input: SyncMode syncmode, string[] cursorfield, JsonElement streamstate | Output: Dictionary<string, object></param>
        /// <returns></returns>
        public FluentStreamBuilder StreamSlices(
            Func<SyncMode, string[], Dictionary<string, object>, Dictionary<string, object>>
                func) =>
            AddFunc(func, nameof(StreamSlices));

        /// <summary>
        /// Override the parse response by parsing an array that can be found using JSONPath
        /// </summary>
        /// <param name="path"></param>
        /// <returns></returns>
        public FluentStreamBuilder ParseResponseArray(string path) => ParseResponse((response, _, _, _) =>
        {
            var responseobject = response.GetStringAsync().Result.AsJsonElement();
            List<JsonElement> toreturn = new List<JsonElement>();
            foreach (var item in JsonSelector.Select(responseobject, path))
                if(item.ValueKind == JsonValueKind.Array)
                    foreach (var subobject in item.EnumerateArray())
                        toreturn.Add(subobject);

            return toreturn;
        });

        /// <summary>
        /// Override the parse response by parsing an object that can be found using JSONPath
        /// </summary>
        /// <param name="path"></param>
        /// <returns></returns>
        public FluentStreamBuilder ParseResponseObject(string path) => ParseResponse((response, _, _, _) =>
        {
            var responseobject = response.GetStringAsync().Result.AsJsonElement();
            List<JsonElement> toreturn = new List<JsonElement>();
            foreach (var item in JsonSelector.Select(responseobject, path))
                toreturn.Add(item);

            return toreturn.Count > 0 ? new[] { toreturn.First() } : Array.Empty<JsonElement>();
        });

        /// <summary>
        /// URL base for the  API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "https://myapi.com/v1/"
        /// </summary>
        /// <returns></returns>
        public FluentStreamBuilder UrlBase(Func<string> func) => AddFunc(func, nameof(UrlBase));

        /// <summary>
        /// Override if needed. Specifies timeout period for a request.
        /// </summary>
        /// <returns></returns>
        public FluentStreamBuilder TimeOut(TimeSpan timeout) => AddProperty(timeout, nameof(AddProperty));

        /// <summary>
        /// Decides how often to checkpoint state (i.e: emit a STATE message). E.g: if this returns a value of 100, then state is persisted after reading
        /// 100 records, then 200, 300, etc.. A good default value is 1000 although your mileage may vary depending on the underlying data source.
        /// 
        /// Checkpointing a stream avoids re-reading records in the case a sync is failed or cancelled.
        /// 
        /// return None if state should not be checkpointed e.g: because records returned from the underlying data source are not returned in
        /// ascending order with respect to the cursor field. This can happen if the source does not support reading records in ascending order of
        /// created_at date (or whatever the cursor is). In those cases, state must only be saved once the full stream has been read.
        /// </summary>
        public FluentStreamBuilder StateCheckpointInterval(int? interval) => AddProperty(interval, nameof(StateCheckpointInterval));

        /// <summary>
        /// Most HTTP streams use a source defined cursor (i.e: the user can't configure it like on a SQL table)
        /// </summary>
        /// <param name="value"></param>
        /// <returns></returns>
        public FluentStreamBuilder SourceDefinedCursor(bool value) => AddProperty(value, nameof(SourceDefinedCursor));

        /// <summary>
        /// Use this variable to define page size for API http requests with pagination support
        /// </summary>
        /// <param name="value"></param>
        public FluentStreamBuilder PageSize(int? value) => AddProperty(value, nameof(PageSize));

        /// <summary>
        /// Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        /// </summary>
        /// <param name="value"></param>
        /// <returns></returns>
        public FluentStreamBuilder HttpMethod(HttpMethod value) => AddProperty(value, nameof(HttpMethod));

        /// <summary>
        /// Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        /// </summary>
        /// <param name="value"></param>
        /// <returns></returns>
        public FluentStreamBuilder RaiseOnHttpErrors(bool value) => AddProperty(value, nameof(RaiseOnHttpErrors));

        /// <summary>
        /// Override if needed. Specifies maximum amount of retries for backoff policy. Return 0 for no limit.
        /// </summary>
        /// <param name="value"></param>
        /// <returns></returns>
        public FluentStreamBuilder MaxRetries(int value) => AddProperty(value, nameof(MaxRetries));

        /// <summary>
        /// Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        /// </summary>
        /// <returns>The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.</returns>
        public FluentStreamBuilder CursorField(string[] value) => AddProperty(value, nameof(CursorField));

        /// <summary>
        /// Set the authentication implementation for this stream
        /// </summary>
        /// <param name="auth"></param>
        /// <returns></returns>
        public FluentStreamBuilder WithAuth(AuthBase auth) => new(Name, _methods, _properties, auth);

        /// <summary>
        /// Have one stream depend on another stream and cache this output as input for the other stream
        /// </summary>
        /// <param name="stream"></param>
        /// <param name="jsonpath"></param>
        /// <param name="currentitems"></param>
        /// <returns></returns>
        public FluentStreamBuilder CacheResultsForStream(string stream, string jsonpath,
            Func<JsonElement[], List<JsonElement>, List<JsonElement>> currentitems) =>
            AddFunc(new Func<Tuple<string, string, Func<JsonElement[], List<JsonElement>, List<JsonElement>>>>(() => Tuple.Create(stream, jsonpath, currentitems)), "CachedFor" + "_" + stream);

        private FluentStreamBuilder AddProperty<T>(T value, string signature) =>
        new(Name, _methods, new List<DynamicProperty>(_properties.Where(x => x.Signature != signature))
        {
            new()
            {
                Value = value,
                FType = typeof(T),
                Signature = signature
            }
        }, _authentication);

        private FluentStreamBuilder AddFunc<T>(T func, string signature) =>
            new(Name, new List<DynamicMethod>(_methods.Where(x => x.Signature != signature))
            {
                new()
                {
                    Body = func,
                    Signature = signature
                }
            }, _properties, _authentication);

        public GenericStream Create(string name) => new(name, _methods, _properties, _authentication);
    }

    public class GenericStream : HttpStream
    {
        private readonly IEnumerable<DynamicMethod> _methods;
        private readonly IEnumerable<DynamicProperty> _properties;

        /// <summary>
        /// Receives any dependent elements from this stream
        /// </summary>
        public Dictionary<string, IReadOnlyList<JsonElement>> CachedElements { get; } = new();

        /// <summary>
        /// Streams the current stream is dependent on
        /// </summary>
        public string[] CachedFor { get; init; }

        public GenericStream(string name, IEnumerable<DynamicMethod> methods, IEnumerable<DynamicProperty> properies, AuthBase auth = null)
        {
            _givenName = name;
            _methods = methods;
            _properties = properies;
            WithAuth(auth);

            //Set CachedFor
            CachedFor = GetCachedFor().Select(x => x.Item1).ToArray();

            //Check for default path 
            if (!methods.Any(x => x.Signature == nameof(Path)))
            {
                var current = _methods.ToList();
                current.Add(new DynamicMethod
                {
                    Body = new Func<JsonElement, Dictionary<string, object>?, Dictionary<string, object>?, string>((_, _, _) => Name),
                    Signature = nameof(Path)
                });
                _methods = current;
            }
            //Check if default nextpagetoken has been implemented
            if (!methods.Any(x => x.Signature == nameof(NextPageToken)))
            {
                var current = _methods.ToList();
                current.Add(new DynamicMethod
                {
                    Body = new Func<IFlurlRequest, IFlurlResponse, Dictionary<string, object>>((_, _) => new Dictionary<string, object>()),
                    Signature = nameof(NextPageToken)
                });
                _methods = current;
            }
        }

        private IEnumerable<Tuple<string, string, Func<JsonElement[], List<JsonElement>, List<JsonElement>>>>
            GetCachedFor() => _methods.Where(x => x.Signature.StartsWith("CachedFor")).Select(x =>
            x.Body as Func<Tuple<string, string,
                Func<JsonElement[], List<JsonElement>, List<JsonElement>>>>).Select(x => x());

        public override bool SourceDefinedCursor
        {
            get => TryGetProperty(nameof(SourceDefinedCursor), out bool value) ? value : base.SourceDefinedCursor;
        }

        public override int? PageSize
        {
            get => TryGetProperty(nameof(PageSize), out int? value) ? value : base.PageSize;
        }

        public override HttpMethod HttpMethod
        {
            get => TryGetProperty(nameof(HttpMethod), out HttpMethod value) ? value : base.HttpMethod;
        }

        public override int? StateCheckpointInterval
        {
            get => TryGetProperty(nameof(StateCheckpointInterval), out int? value) ? value : base.StateCheckpointInterval;
        }

        public override int MaxRetries
        {
            get => TryGetProperty(nameof(MaxRetries), out int value) ? value : base.MaxRetries;
        }

        public override string[] CursorField
        {
            get => TryGetProperty(nameof(CursorField), out string[] value) ? value : base.CursorField;
        }

        public override bool RaiseOnHttpErrors
        {
            get => TryGetProperty(nameof(RaiseOnHttpErrors), out bool value) ? value : base.RaiseOnHttpErrors;
        }

        public override TimeSpan TimeOut
        {
            get => TryGetProperty(nameof(TimeOut), out TimeSpan value) ? value : base.TimeOut;
        }

        private bool TryGetMethod<T>(string signature, out T func)
        {
            if (_methods.Any(x => x.Signature == signature))
            {
                func = (T)_methods.First(x => x.Signature == signature).Body;
                return true;
            }

            func = default;
            return false;
        }

        private bool TryGetProperty<T>(string signature, out T value)
        {
            if (_properties.Any(x => x.Signature == signature && x.FType == typeof(T)))
            {
                value = (T)_properties.First(x => x.Signature == signature && x.FType == typeof(T)).Value;
                return true;
            }

            value = default;
            return false;
        }

        public override TimeSpan BackoffTime(int retryCount, IFlurlResponse response) =>
            TryGetMethod<Func<int, IFlurlResponse, TimeSpan>>(nameof(BackoffTime), out var func)
                ? func.Invoke(retryCount, response)
                : base.BackoffTime(retryCount, response);

        public override string UrlBase() =>
            TryGetMethod<Func<string>>(nameof(UrlBase), out var func)
                ? func.Invoke()
                : throw new NotImplementedException();

        public override Dictionary<string, object> NextPageToken(IFlurlRequest request, IFlurlResponse response) =>
            TryGetMethod<Func<IFlurlRequest, IFlurlResponse, Dictionary<string, object>>>(nameof(NextPageToken), out var func)
                ? func.Invoke(request, response)
                : throw new NotImplementedException();

        public override string Path(JsonElement streamstate,
            Dictionary<string, object> streamslice = null, Dictionary<string, object> nextpagetoken = null) =>
            TryGetMethod<
                Func<JsonElement, Dictionary<string, object>?, Dictionary<string, object>?, String>>(
                nameof(Path), out var func)
                ? func.Invoke(streamstate, streamslice, nextpagetoken)
                : throw new NotImplementedException();

        public override IEnumerable<JsonElement> ParseResponse(IFlurlResponse response,
            JsonElement streamstate, Dictionary<string, object> streamslice = null,
            Dictionary<string, object> nextpagetoken = null)
        {
            var results = TryGetMethod<Func<IFlurlResponse, JsonElement, Dictionary<string, object>?,
                Dictionary<string, object>?, IEnumerable<JsonElement>>>(nameof(ParseResponse), out var func)
                ? func.Invoke(response, streamstate, streamslice, nextpagetoken)
                : throw new NotImplementedException();

            //Set dependent items
            var jsonElements = results as JsonElement[] ?? results.ToArray();
            foreach (var dependent in GetCachedFor())
                foreach (var recordEelement in jsonElements)
                {
                    string stream = dependent.Item1;
                    if (!CachedElements.ContainsKey(stream))
                        CachedElements.Add(stream, new List<JsonElement>());

                    CachedElements[dependent.Item1] =
                        dependent.Item3(JsonSelector.Select(recordEelement, dependent.Item2).ToArray(),
                            CachedElements[dependent.Item1].ToList());
                }

            //Send back the results
            return jsonElements;
        }

        public override bool ShouldRetry(FlurlHttpException exc) =>
            TryGetMethod<Func<FlurlHttpException, bool>>(nameof(ShouldRetry), out var func)
                ? func.Invoke(exc)
                : base.ShouldRetry(exc);

        public override JsonSchema GetJsonSchema() =>
            TryGetMethod<Func<JsonSchema>>(nameof(GetJsonSchema), out var func)
                ? func.Invoke()
                : base.GetJsonSchema();

        public override JsonElement GetUpdatedState(JsonElement currentstreamstate,
            JsonElement latestrecord) =>
            TryGetMethod<Func<JsonElement, JsonElement, JsonElement>>(
                nameof(GetUpdatedState), out var func)
                ? func.Invoke(currentstreamstate, latestrecord)
                : base.GetUpdatedState(currentstreamstate, latestrecord);

        public override Task<long> ReadRecords(AirbyteLogger logger, SyncMode syncMode, ChannelWriter<AirbyteMessage> streamchannel,
            JsonElement streamstate,
            long? recordlimit = null,
            string[] cursorfield = null, Dictionary<string, object> streamslice = null) =>
            TryGetMethod<Func<AirbyteLogger, SyncMode, ChannelWriter<AirbyteMessage>, JsonElement, long?, string[],
                Dictionary<string, object>, Task<long>>>(nameof(ReadRecords), out var func)
                ? func.Invoke(logger, syncMode, streamchannel, streamstate, recordlimit, cursorfield, streamslice)
                : base.ReadRecords(logger, syncMode, streamchannel, streamstate, recordlimit, cursorfield, streamslice);

        public override string RequestBodyData(JsonElement streamstate,
            Dictionary<string, object> streamslice = null, Dictionary<string, object> nextpagetoken = null) =>
            TryGetMethod<Func<JsonElement, Dictionary<string, object>, Dictionary<string, object>,
                string>>(nameof(RequestBodyData), out var func)
                ? func.Invoke(streamstate, streamslice, nextpagetoken)
                : base.RequestBodyData(streamstate, streamslice, nextpagetoken);

        public override string RequestBodyJson(JsonElement streamstate,
            Dictionary<string, object> streamslice = null, Dictionary<string, object> nextpagetoken = null) =>
            TryGetMethod<Func<JsonElement, Dictionary<string, object>, Dictionary<string, object>,
                string>>(nameof(RequestBodyJson), out var func)
                ? func.Invoke(streamstate, streamslice, nextpagetoken)
                : base.RequestBodyJson(streamstate, streamslice, nextpagetoken);

        public override Dictionary<string, object> RequestHeaders(JsonElement streamstate,
            Dictionary<string, object> streamslice = null, Dictionary<string, object> nextpagetoken = null) =>
            TryGetMethod<Func<JsonElement, Dictionary<string, object>, Dictionary<string, object>,
                Dictionary<string, object>>>(nameof(RequestHeaders), out var func)
                ? func.Invoke(streamstate, streamslice, nextpagetoken)
                : base.RequestHeaders(streamstate, streamslice, nextpagetoken);

        public override Dictionary<string, object> RequestParams(JsonElement streamstate,
            Dictionary<string, object> streamslice = null, Dictionary<string, object> nextpagetoken = null) =>
            TryGetMethod<Func<JsonElement, Dictionary<string, object>, Dictionary<string, object>,
                Dictionary<string, object>>>(nameof(RequestParams), out var func)
                ? func.Invoke(streamstate, streamslice, nextpagetoken)
                : base.RequestParams(streamstate, streamslice, nextpagetoken);

        public override Dictionary<string, object> StreamSlices(SyncMode syncmode,
            string[] cursorfield, JsonElement streamstate) =>
            TryGetMethod<Func<SyncMode, string[], JsonElement,
                Dictionary<string, object>>>(nameof(StreamSlices), out var func)
                ? func.Invoke(syncmode, cursorfield, streamstate)
                : base.StreamSlices(syncmode, cursorfield, streamstate);
    }
}