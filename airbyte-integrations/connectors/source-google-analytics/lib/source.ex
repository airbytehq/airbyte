defmodule Airbyte.Source.GoogleAnalytics.Source do
  @behaviour Airbyte.Source

  alias Airbyte.Protocol.{
    AirbyteCatalog,
    AirbyteConnectionStatus,
    ConnectorSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.{Client, ConnectionSpecification, Streams}
  alias Airbyte.Source.GoogleAnalytics.Commands.Read

  alias GoogleApi.Analytics.V3.Api.Management
  alias GoogleApi.Analytics.V3.Model.AccountSummaries

  @streams [
    Streams.Accounts.stream(),
    Streams.Profiles.stream(),
    Streams.WebProperties.stream()
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
        @streams,
        @reports |> Enum.map(&Streams.Reports.stream(&1, fields)),
        configured_reports(spec) |> Enum.map(&Streams.Reports.stream(&1, fields))
      ]

      {:ok, AirbyteCatalog.create(streams |> List.flatten())}
    end
  end

  @impl Airbyte.Source
  def read(options), do: options |> Read.run()

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
