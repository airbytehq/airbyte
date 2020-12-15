defmodule Airbyte.Protocol.AirbyteStateMessage do
  @moduledoc """
  Specification of an AirbyteStateMessage
  https://github.com/airbytehq/airbyte/blob/master/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml
  """
  use TypedStruct

  @derive Jason.Encoder

  typedstruct do
    @typedoc "Specification of an AirbyteStateMessage"

    field(:data, any(), enforce: true)
  end
end
