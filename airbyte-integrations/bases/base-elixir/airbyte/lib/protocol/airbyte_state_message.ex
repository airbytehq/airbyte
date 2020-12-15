defmodule Airbyte.Protocol.AirbyteStateMessage do
  @moduledoc """
  Specification of an AirbyteStateMessage
  https://github.com/airbytehq/airbyte/blob/master/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml
  """
  use TypedStruct

  alias Airbyte.Helpers

  @derive Jason.Encoder

  typedstruct do
    @typedoc "Specification of an AirbyteStateMessage"

    field(:data, any(), enforce: true)
  end

  def from_file(path) do
    Helpers.json_to_struct(path, __MODULE__)
  end
end
