defmodule Airbyte.Source.GoogleAnalytics.Commands.Read do
  alias Airbyte.Protocol.{
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    ConnectionSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.{
    ConnectionSpecification,
    GoogleAnalytics
  }

  def run(
        config: %ConnectionSpecification{} = config,
        catalog: %ConfiguredAirbyteCatalog{} = catalog
      ) do
    # IO.inspect({config, catalog})

    stream =
      [AirbyteRecordMessage.new("stream-name", %{users: 1})]
      |> Stream.map(&Function.identity/1)

    {:ok, stream}
  end
end
