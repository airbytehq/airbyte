using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Airbyte.Cdk;
using Airbyte.Cdk.Sources;
using Airbyte.Cdk.Sources.Streams;
using Airbyte.Cdk.Sources.Utils;
using Flurl;
using Flurl.Http;

namespace source_exchange_rates
{
    public class ExchangeRates : AbstractSource
    {
        public static async Task Main(string[] args) => await AirbyteEntrypoint.Main(args);

        public string UrlBase => "https://api.exchangerate.host";

        public override bool CheckConnection(AirbyteLogger logger, JsonDocument config, out Exception exc)
        {
            exc = null;
            try
            {
                return UrlBase.AppendPathSegment("latest")
                    .GetAsync()
                    .Result.GetJsonAsync().Result.success;
            }
            catch (Exception e)
            {
                exc = e;
            }

            return false;
        }

        public override Stream[] Streams(JsonDocument config)
        {
            var baseimpl = UrlBase.HttpStream().ParseResponseObject("$");
            var baseimpl_symbols = baseimpl
                //.CacheResultsForStream("historical", "$.symbols[*].code", (jsondocument, _) => jsondocument.ToList()) TODO: cannot handle dependencies... yet
                .Create("symbols");
            var vatrates = baseimpl.Create("vat_rates");

            DateTime? _lastDateTime = null;
            string _currentsymbol = "";
            string[] _configuredsymbols = config.RootElement.TryGetProperty("base", out var symbols)
                ? symbols.GetString().Split(",").Select(x => x.Replace(" ", "").ToUpper()).ToArray()
                : Array.Empty<string>();
            Dictionary<string, DateTime> _currentstate = new Dictionary<string, DateTime>();

            var incrementalimpl = baseimpl
                .CursorField(new[] { "date" })
                .BackoffTime(((i, _) => TimeSpan.FromMinutes(i * 10)))
                .GetUpdatedState((_, _) => _currentstate.AsJsonDocument())
                .NextPageToken((request, _) =>
                {
                    DateTime date = DateTime.Parse(request.Url.PathSegments[0]);
                    var symbol = request.Url.QueryParams.FirstOrDefault("base").ToString();
                    if (date >= DateTime.Today.AddDays(-1))
                    {
                        var symbols = _configuredsymbols.Length > 0
                            ? _configuredsymbols.ToList()
                            : new List<string> { "EUR" };
                        int symbolnr = symbols.FindIndex(x => x == symbol) + 1;
                        if (symbolnr == symbols.Count)
                            return null;
                        symbol = symbols[symbolnr];
                        _currentsymbol = symbol;
                        _lastDateTime = null;
                    }
                    else
                        _currentstate[symbol] = date;

                    return new Dictionary<string, object> { { "symbol", symbol } };
                })
                .Path((state, _, nextpagetoken) =>
                {
                    var inputstate = state.ToType<Dictionary<string, DateTime>>();
                    if (inputstate.Count > 0 && _currentstate.Count == 0)
                        _currentstate = inputstate;

                    if (nextpagetoken != null && _currentstate.ContainsKey(nextpagetoken["symbol"].ToString()))
                    {
                        DateTime dt = _currentstate[nextpagetoken["symbol"].ToString()].AddDays(1);
                        if (_lastDateTime.HasValue && _lastDateTime >= dt)
                            dt = _lastDateTime.Value.AddDays(1);

                        _lastDateTime = dt;
                        return dt.ToString("yyyy-MM-dd");
                    }
                    else if (nextpagetoken == null && _currentstate.Count > 0)
                        return _currentstate.Min(x => x.Value).ToString("yyyy-MM-dd");
                    else
                        return config.RootElement.TryGetProperty("start_date", out var startdate) ? startdate.GetString() : "2008-01-01";
                })
                .RequestParams((_, _, nextpagetoken) => new Dictionary<string, object>
                {
                    {
                        "base", nextpagetoken != null
                        ? nextpagetoken["symbol"]
                        : _configuredsymbols.Length > 0
                            ? _configuredsymbols[0]
                            : "EUR"
                    }
                })
                .Create("historical");

            return new Stream[]
            {
                baseimpl_symbols,
                vatrates,
                incrementalimpl
            };
        }
    }
}
