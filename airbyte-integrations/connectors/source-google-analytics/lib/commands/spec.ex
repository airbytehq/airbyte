defmodule Airbyte.Source.GoogleAnalytics.Commands.Spec do
  alias Airbyte.Protocol.{
    AirbyteMessage,
    ConnectorSpecification
  }

  @connection_spec "priv/connection_specification.json"
                   |> Path.absname()
                   |> File.read!()
                   |> Jason.decode!()

  def run() do
    connector_spec() |> AirbyteMessage.dispatch()

    :ok
  end

  defp connector_spec() do
    %ConnectorSpecification{
      documentationUrl: "http://documentation.example",
      changelogUrl: "http://changelogurl.example",
      connectionSpecification: @connection_spec,
      supportsIncremental: true
    }
  end
end
