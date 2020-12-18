defmodule Airbyte.Source.GoogleAnalytics.Streams.Profiles do
  @moduledoc "Profiles Stream"
  use TypedStruct

  alias Airbyte.Protocol.{AirbyteStream, AirbyteRecordMessage}

  alias GoogleApi.Analytics.V3.Model.{
    AccountSummary,
    ProfileSummary,
    WebPropertySummary
  }

  @derive Jason.Encoder

  @name "profiles"
  @schema "priv/streams/profiles.json"
          |> Path.absname()
          |> File.read!()
          |> Jason.decode!()

  typedstruct do
    field(:id, String.t(), enforce: true)
    field(:name, String.t(), enforce: true)
    field(:type, String.t(), enforce: true)
    field(:account_id, String.t(), enforce: true)
    field(:web_property_id, String.t(), enforce: true)
  end

  def stream() do
    %AirbyteStream{
      name: @name,
      json_schema: Map.put_new(@schema, :description, __MODULE__),
      supported_sync_modes: ["full_refresh"],
      source_defined_cursor: false
    }
  end

  def new(
        %AccountSummary{id: account_id},
        %WebPropertySummary{id: property_id} = property,
        %ProfileSummary{} = summary
      ) do
    %__MODULE__{
      id: summary.id,
      name: summary.name,
      type: summary.type,
      account_id: account_id,
      web_property_id: property_id
    }
  end

  def record(%__MODULE__{} = stream) do
    AirbyteRecordMessage.new(@name, Map.from_struct(stream))
  end
end
