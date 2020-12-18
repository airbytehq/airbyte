defmodule Airbyte.Source.GoogleAnalytics.Streams.Reports do
  @moduledoc "Accounts Stream"
  use TypedStruct

  alias Airbyte.Protocol.{AirbyteStream}
  alias Airbyte.Source.GoogleAnalytics.Types

  @derive Jason.Encoder

  typedstruct do
    field(:name, String.t(), enforce: true)
    field(:metrics, list(String.t()), enforce: true)
    field(:dimensions, list(String.t()), enforce: true)
    field(:cursor, String.t(), enforce: true)
  end

  def stream(report, fields) do
    default_cursor_field =
      case report.cursor do
        nil -> nil
        cursor -> cursor
      end

    %AirbyteStream{
      name: report.name,
      json_schema: schema(report, fields),
      supported_sync_modes: ["full_refresh", "incremental"],
      default_cursor_field: default_cursor_field,
      source_defined_cursor: is_nil(default_cursor_field) == false
    }
  end

  def from_file(path) do
    Airbyte.Helpers.json_to_struct(path, __MODULE__)
  end

  defp schema(%__MODULE__{} = report, fields) do
    properties = report.metrics |> Enum.map(&to_property(&1, fields)) |> Enum.into(%{})

    %{
      "$schema": "http://json-schema.org/draft-07/schema#",
      "$id":
        "https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-google-analytics/priv/reports/#{
          report.name
        }.json",
      description: __MODULE__,
      additionalProperties: false,
      title: report.name,
      type: "object",
      properties: properties
    }
  end

  defp to_property(name, fields) do
    id = Types.to_camel_case(name)

    fields = %{
      "type" => fields[name].dataType |> Types.to_jsonschema_type(),
      "description" => name
    }

    {id, fields}
  end
end
