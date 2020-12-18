defmodule Airbyte.Source do
  alias Airbyte.Protocol.{
    ConfiguredAirbyteCatalog,
    ConnectionStatus,
    ConnectorSpecification
  }

  @type read_options :: [
          config: ConnectorSpecification.t(),
          catalog: ConfiguredAirbyteCatalog.t()
        ]

  @callback check(map) :: {:ok, ConnectionStatus.t()} | {:error, String.t()}
  @callback discover(map) :: {:ok, AirbyteCatalog.t()} | {:error, String.t()}
  @callback read(read_options()) :: {:ok, Stream.t()} | {:error, String.t()}
  @callback spec() :: {:ok, map} | {:error, String.t()}
  @callback connection_specification() :: any()
end
