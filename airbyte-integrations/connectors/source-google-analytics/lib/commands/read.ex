defmodule Airbyte.Source.GoogleAnalytics.Commands.Read do
  alias Airbyte.Protocol.{
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectionSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.{
    ConnectionSpecification,
    Client,
    DataRequest,
    Streams
  }

  alias GoogleApi.Analytics.V3.Api.{Data, Management, Metadata}

  alias GoogleApi.Analytics.V3.Model.{
    AccountSummary,
    GaData,
    WebPropertySummary,
    ProfileSummary
  }

  def run(
        config: %ConnectionSpecification{} = spec,
        catalog: %ConfiguredAirbyteCatalog{} = catalog,
        state: state
      ) do
    # stream =
    #   Stream.concat(
    #     static_streams(spec)
    #     catalog.streams |> process_stream(spec, &1, state)
    #   )
    #   |> Stream.filter()

    # stream = catalog.streams |> Stream.map(&process_stream(spec, &1, state))

    {:ok, conn} = Client.connection(spec)

    metrics = [
      "ga:users",
      "ga:newUsers",
      "ga:sessions",
      "ga:sessionsPerUser",
      "ga:pageviews",
      "ga:pageviewsPerSession",
      "ga:avgSessionDuration",
      "ga:bounceRate"
    ]

    # {:ok, d} =
    #   get_data(
    #     conn,
    #     "93282827",
    #     "2015-01-01",
    #     "2020-12-01",
    #     metrics,
    #     ["ga:date"]
    #   )

    ["1"]
    |> Stream.cycle()
    |> Stream.map(fn _ ->
      IO.write(".")

      request = %DataRequest{
        profile_id: "93282827",
        start_date: "2015-01-01",
        end_date: "2020-12-01",
        metrics: metrics,
        dimensions: ["ga:date"]
      }

      conn |> DataRequest.query(request)
    end)
    |> Stream.run()

    stream = static_streams(spec)
    # stream =
    #   [AirbyteRecordMessage.new("test", %{hello: true})]
    #   |> Stream.map(&Function.identity/1)

    {:ok, stream}
  end

  def process_stream(
        %ConnectionSpecification{} = spec,
        %ConfiguredAirbyteStream{} = stream,
        state
      ) do
    case stream.stream.name do
      "accounts" -> nil
      # "profiles" -> process_stream_profiles(spec)
      # "web_properties" -> process_stream_web_properties(spec)
      _ -> nil
    end
  end

  defp static_streams(%ConnectionSpecification{} = spec) do
    with {:ok, conn} <- Client.connection(spec),
         {:ok, summary} <- Management.analytics_management_account_summaries_list(conn) do
      summary.items |> Enum.map(&process_account/1) |> List.flatten()
    end
  end

  defp process_account(%AccountSummary{} = account) do
    record = Streams.Accounts.new(account) |> Streams.Accounts.record()
    properties = Enum.map(account.webProperties, &process_web_property(account, &1))

    [record] ++ properties
  end

  defp process_web_property(%AccountSummary{} = account, %WebPropertySummary{} = property) do
    record = Streams.WebProperties.new(account, property) |> Streams.WebProperties.record()
    profiles = Enum.map(property.profiles, &process_profile(account, property, &1))

    [record] ++ profiles
  end

  defp process_profile(
         %AccountSummary{} = account,
         %WebPropertySummary{} = property,
         %ProfileSummary{} = profile
       ) do
    Streams.Profiles.new(account, property, profile) |> Streams.Profiles.record()
  end
end
