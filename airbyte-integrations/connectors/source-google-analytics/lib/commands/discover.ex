defmodule Airbyte.Source.GoogleAnalytics.Commands.Discover do
  alias Airbyte.Protocol.{
    AirbyteCatalog,
    ConnectorSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.Apis.Api

  def run(%ConnectorSpecification{} = spec) do
    streams =
      Api.impl()
      |> Keyword.values()
      |> Enum.map(& &1.discover(spec))
      |> List.flatten()

    %AirbyteCatalog{streams: streams}
  end
end
