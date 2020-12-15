defmodule Airbyte.Source.GoogleAnalytics.Commands.Discover do
  alias Airbyte.Protocol.{
    AirbyteCatalog,
    AirbyteStream
  }

  alias Airbyte.Source.GoogleAnalytics.{
    ConnectionSpecification,
    GoogleAnalytics
  }

  alias GoogleApi.Analytics.V3.Api.{Management, Metadata}
  alias GoogleApi.Analytics.V3.Connection
  alias GoogleApi.Analytics.V3.Model.{Column, Columns}

  # def run(%ConnectorSpecification{} = spec) do
  #   streams =
  #     Api.impl()
  #     |> Keyword.values()
  #     |> Enum.map(& &1.discover(spec))
  #     |> List.flatten()

  #   %AirbyteCatalog{streams: streams}
  # end

  def run(%ConnectionSpecification{} = spec) do
    get_standard_dimensions(spec)
    |> IO.inspect()

    {:ok,
     %AirbyteCatalog{
       streams: [
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
     }}
  end

  defp get_standard_dimensions(%ConnectionSpecification{} = spec) do
    with {:ok, conn} <- spec |> GoogleAnalytics.connection(),
         {:ok, columns} <- Metadata.analytics_metadata_columns_list(conn, "ga") do
      # columns.items
      # |> Enum.map(fn %Column{} = col -> [col[:id]: col["dataType"] end)
      columns
    end
  end
end
