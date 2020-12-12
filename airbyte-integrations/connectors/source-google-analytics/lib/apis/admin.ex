defmodule Airbyte.Source.GoogleAnalytics.Apis.Admin do
  alias Airbyte.Protocol.{ConnectorSpecification}
  alias Airbyte.Source.GoogleAnalytics.Apis.Api
  alias GoogleApi.AnalyticsAdmin.V1alpha.Connection
  alias GoogleApi.AnalyticsAdmin.V1alpha.Api.AccountSummaries

  @behaviour Api

  @impl Api
  def connection_status(%Goth.Token{token: token} = _) do
    with conn <- token |> Connection.new(),
         {:ok, _} <-
           AccountSummaries.analyticsadmin_account_summaries_list(conn) do
      __MODULE__ |> Api.connection_status(:ok)
    else
      error ->
        __MODULE__ |> Api.connection_status(error)
    end
  end

  @impl Api
  def discover(%ConnectorSpecification{} = _spec), do: []
end
