defmodule Airbyte.Source.GoogleAnalytics do
  @behaviour Airbyte.Source

  alias Airbyte.Protocol.{
    AirbyteMessage,
    ConnectorSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.Commands.{
    Check,
    Discover,
    Spec,
    Read
  }

  @impl Airbyte.Source
  def check(%ConnectorSpecification{} = spec) do
    spec
    |> Check.run()
    |> AirbyteMessage.dispatch()
  end

  @impl Airbyte.Source
  def discover(%ConnectorSpecification{} = spec) do
    spec
    |> Discover.run()
    |> AirbyteMessage.dispatch()
  end

  @impl Airbyte.Source
  def read(options), do: Read.run(options)

  @impl Airbyte.Source
  def spec(), do: Spec.run()
end
