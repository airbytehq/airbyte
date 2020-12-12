defmodule Airbyte.Protocol.ConnectorSpecification do
  @moduledoc """
  Specification of a connector (source/destination)
  https://github.com/airbytehq/airbyte/blob/master/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml
  """
  use TypedStruct

  alias Airbyte.Source.GoogleAnalytics.Helpers

  @derive Jason.Encoder

  typedstruct do
    @typedoc "Specification of a connector (source/destination)"

    field(:documentationUrl, String.t())
    field(:changelogUrl, String.t())
    field(:connectionSpecification, map(), enforce: true)
    field(:supportsIncremental, boolean())
  end

  def from_file(path) do
    Helpers.json_to_struct(path, __MODULE__)
  end
end
