defmodule Airbyte.Source.GoogleAnalytics.Apis.Analytics do
  alias Airbyte.Protocol.{AirbyteStream, ConnectorSpecification}
  alias Airbyte.Source.GoogleAnalytics.Apis.Api
  alias GoogleApi.Analytics.V3.Api.{Management, Metadata}
  alias GoogleApi.Analytics.V3.Connection
  alias GoogleApi.Analytics.V3.Model.{Column, Columns}

  @behaviour Api

  @impl Api
  def connection_status(%Goth.Token{token: token} = _) do
    with conn <- token |> Connection.new(),
         {:ok, _} <-
           Management.analytics_management_account_summaries_list(conn, "max-results": 1) do
      __MODULE__ |> Api.connection_status(:ok)
    else
      error ->
        __MODULE__ |> Api.connection_status(error)
    end
  end

  @impl Api
  def discover(%ConnectorSpecification{} = spec) do
    get_standard_dimensions(spec)
    |> IO.inspect()

    [
      %AirbyteStream{
        name: "analytics",
        json_schema: %{},
        supported_sync_modes: ["incremental", "full_refresh"],
        # not sure
        source_defined_cursor: true,
        # not sure
        default_cursor_field: nil
      }
    ]
  end

  defp get_standard_dimensions(%ConnectorSpecification{} = spec) do
    with conn <- spec |> connection(),
         {:ok, columns} <- Metadata.analytics_metadata_columns_list(conn, "ga") do
      # columns.items
      # |> Enum.map(fn %Column{} = col -> [col[:id]: col["dataType"] end)
      columns
    end
  end

  # defp get_custom_dimensions(%ConnectorSpecification{} = spec) do
  #   spec
  #   |> connection()
  #   |> Management.analytics_management_custom_dimensions_list(
  #     account_id(spec),
  #     property_id(spec)
  #   )
  # end

  defp connection(%ConnectorSpecification{} = spec) do
    with {:ok, %Goth.Token{token: token}} <- spec |> Api.get_token() do
      token |> Connection.new()
    end
  end

  defp account_id(%ConnectorSpecification{} = spec) do
    spec.connectionSpecification.account_id
  end

  defp property_id(%ConnectorSpecification{} = spec) do
    spec.connectionSpecification.account_id
  end
end
