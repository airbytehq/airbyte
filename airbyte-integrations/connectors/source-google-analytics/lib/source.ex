defmodule Airbyte.Source.GoogleAnalytics.Source do
  @behaviour Airbyte.Source

  alias Airbyte.Protocol.{
    AirbyteCatalog,
    AirbyteConnectionStatus,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.{Client, ConnectionSpecification, Streams}
  alias GoogleApi.Analytics.V3.Api.Management
  alias GoogleApi.Analytics.V3.Model.AccountSummaries

  @streams [
    Streams.Accounts,
    Streams.Profiles,
    Streams.WebProperties
  ]

  @reports [
    "priv/reports/audience-overview.json" |> Streams.Reports.from_file()
  ]

  @connection_spec "priv/connection_specification.json"
                   |> Path.absname()
                   |> File.read!()
                   |> Jason.decode!()

  @impl Airbyte.Source
  def check(%ConnectionSpecification{} = spec) do
    with {:ok, conn} <- Client.connection(spec),
         {:ok, %AccountSummaries{username: user}} <-
           Management.analytics_management_account_summaries_list(conn, "max-results": 1) do
      {:ok, AirbyteConnectionStatus.succeeded("Authenticated as #{user}")}
    else
      error -> {:error, error |> Client.get_error_message()}
    end
  end

  @impl Airbyte.Source
  def discover(%ConnectionSpecification{} = spec) do
    with {:ok, conn} <- Client.connection(spec) do
      fields = Client.get_fields_schema(conn)

      streams = [
        @streams |> Enum.map(& &1.stream()),
        @reports |> Enum.map(&Streams.Reports.stream(&1, fields)),
        configured_reports(spec) |> Enum.map(&Streams.Reports.stream(&1, fields))
      ]

      {:ok, AirbyteCatalog.create(streams |> List.flatten())}
    end
  end

  @impl Airbyte.Source
  def read(
        config: %ConnectionSpecification{} = spec,
        catalog: %ConfiguredAirbyteCatalog{} = _catalog,
        state: state
      ) do
    streams = [
      @streams |> Stream.flat_map(& &1.read(spec)),
      @reports |> Stream.flat_map(&Streams.Reports.read(spec, &1, state)),
      configured_reports(spec) |> Stream.flat_map(&Streams.Reports.read(spec, &1, state))
    ]

    {:ok, Stream.flat_map(streams, &Function.identity/1)}
  end

  @impl Airbyte.Source
  def spec() do
    {:ok,
     %ConnectorSpecification{
       documentationUrl:
         "https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-google-analytics/README.md",
       changelogUrl:
         "https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-google-analytics/CHANGELOG.md",
       connectionSpecification: @connection_spec,
       supportsIncremental: true
     }}
  end

  @impl Airbyte.Source
  def connection_specification() do
    Airbyte.Source.GoogleAnalytics.ConnectionSpecification
  end

  defp configured_reports(spec) when is_binary(spec.reports) do
    case Jason.decode(spec.reports) do
      {:ok, reports} -> reports
      _ -> []
    end
  end

  defp configured_reports(_), do: []
end
