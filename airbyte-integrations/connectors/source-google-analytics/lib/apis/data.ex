defmodule Airbyte.Source.GoogleAnalytics.Apis.Data do
  alias Airbyte.Protocol.{ConnectorSpecification}
  alias Airbyte.Source.GoogleAnalytics.Apis.Api
  alias GoogleApi.AnalyticsData.V1alpha.Connection
  alias GoogleApi.AnalyticsData.V1alpha.Api.Properties

  @behaviour Api

  @impl Api
  def connection_status(%Goth.Token{token: token} = _) do
    with conn <- token |> Connection.new(),
         {:ok, _} <-
           Properties.analyticsdata_properties_get_metadata(
             conn,
             "properties/0/metadata"
           ) do
      __MODULE__ |> Api.connection_status(:ok)
    else
      error ->
        __MODULE__ |> Api.connection_status(error)
    end
  end

  @impl Api
  def discover(%ConnectorSpecification{} = _spec), do: []
end
