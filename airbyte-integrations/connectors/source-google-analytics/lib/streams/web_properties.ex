defmodule Airbyte.Source.GoogleAnalytics.Streams.WebProperties do
  @moduledoc "Web Properties Stream"
  use TypedStruct

  alias Airbyte.Protocol.{AirbyteStream, AirbyteRecordMessage}
  alias GoogleApi.Analytics.V3.Model.{AccountSummary, WebPropertySummary}

  @derive Jason.Encoder

  @name "web_properties"
  @schema "priv/stream_web_properties.json"
          |> Path.absname()
          |> File.read!()
          |> Jason.decode!()

  typedstruct do
    field(:id, String.t(), enforce: true)
    field(:name, String.t(), enforce: true)
    field(:level, String.t(), enforce: true)
    field(:website_url, String.t(), enforce: true)
    field(:account_id, String.t(), enforce: true)
  end

  def stream() do
    %AirbyteStream{
      name: @name,
      json_schema: @schema,
      supported_sync_modes: ["full_refresh"]
    }
  end

  def new(%AccountSummary{id: account_id}, %WebPropertySummary{} = property) do
    %__MODULE__{
      id: property.id,
      name: property.name,
      level: property.level,
      website_url: property.websiteUrl,
      account_id: account_id
    }
  end

  def record(%__MODULE__{} = stream) do
    AirbyteRecordMessage.new(@name, Map.from_struct(stream))
  end
end
