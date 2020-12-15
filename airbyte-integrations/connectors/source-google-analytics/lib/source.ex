defmodule Airbyte.Source.GoogleAnalytics.Source do
  @behaviour Airbyte.Source

  alias Airbyte.Protocol.{
    AirbyteConnectionStatus,
    ConnectorSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.{GoogleAnalytics, ConnectionSpecification}
  alias Airbyte.Source.GoogleAnalytics.Commands.{Discover, Read}

  alias GoogleApi.Analytics.V3.Api.Management
  alias GoogleApi.Analytics.V3.Model.AccountSummaries

  @connection_spec "priv/connection_specification.json"
                   |> Path.absname()
                   |> File.read!()
                   |> Jason.decode!()

  @impl Airbyte.Source
  def check(%ConnectionSpecification{} = spec) do
    with {:ok, conn} <- GoogleAnalytics.connection(spec),
         {:ok, %AccountSummaries{username: user}} <-
           Management.analytics_management_account_summaries_list(conn, "max-results": 1) do
      {:ok, AirbyteConnectionStatus.succeeded("Authenticated as #{user}")}
    else
      error -> {:error, error |> GoogleAnalytics.get_error_message()}
    end
  end

  @impl Airbyte.Source
  def discover(%ConnectionSpecification{} = spec) do
    spec |> Discover.run()
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
end
