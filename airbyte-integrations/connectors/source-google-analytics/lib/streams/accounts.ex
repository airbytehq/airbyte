defmodule Airbyte.Source.GoogleAnalytics.Streams.Accounts do
  @moduledoc "Accounts Stream"
  use TypedStruct

  alias Airbyte.Protocol.{AirbyteStream, AirbyteRecordMessage}
  alias GoogleApi.Analytics.V3.Model.AccountSummary

  @derive Jason.Encoder

  @name "accounts"
  @schema "priv/streams/accounts.json"
          |> Path.absname()
          |> File.read!()
          |> Jason.decode!()

  typedstruct do
    field(:id, String.t(), enforce: true)
    field(:name, String.t(), enforce: true)
  end

  def stream() do
    %AirbyteStream{
      name: @name,
      json_schema: @schema,
      supported_sync_modes: ["full_refresh"]
    }
  end

  def new(%AccountSummary{id: id, name: name}) do
    %__MODULE__{id: id, name: name}
  end

  def record(%__MODULE__{} = stream) do
    AirbyteRecordMessage.new(@name, Map.from_struct(stream))
  end
end
