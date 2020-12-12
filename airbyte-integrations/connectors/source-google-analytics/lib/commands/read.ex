defmodule Airbyte.Source.GoogleAnalytics.Commands.Read do
  alias Airbyte.Protocol.{
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification
  }

  def run(
        config: %ConnectorSpecification{} = config,
        catalog: %ConfiguredAirbyteCatalog{} = catalog
      ) do
    IO.inspect({config, catalog})
    # spec() |> AirbyteMessage.dispatch()

    :ok
  end
end
