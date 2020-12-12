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

  @callback check(ConnectorSpecification.t()) ::
              {:ok, ConnectionStatus.t()} | {:error, String.t()}
  @callback discover(ConnectorSpecification.t()) :: :ok | {:error, String.t()}
  @callback read(read_options()) :: :ok | {:error, String.t()}
  @callback spec() :: :ok | {:error, String.t()}
end
