defmodule Airbyte.Source.GoogleAnalytics.Apis.Reporting do
  alias Airbyte.Protocol.{ConnectorSpecification}
  alias Airbyte.Source.GoogleAnalytics.Apis.Api
  alias GoogleApi.AnalyticsReporting.V4.Connection
  alias GoogleApi.AnalyticsReporting.V4.Api.Reports

  @behaviour Api

  @impl Api
  def connection_status(%Goth.Token{token: token} = _) do
    with conn <- token |> Connection.new(),
         {:ok, _} <-
           Reports.analyticsreporting_reports_batch_get(conn) do
      __MODULE__ |> Api.connection_status(:ok)
    else
      error ->
        __MODULE__ |> Api.connection_status(error)
    end
  end

  @impl Api
  def discover(%ConnectorSpecification{} = _spec), do: []
end
