defmodule Airbyte.Source.GoogleAnalytics.Commands.Check do
  alias Airbyte.Protocol.{
    AirbyteConnectionStatus,
    AirbyteLogMessage,
    AirbyteMessage,
    ConnectorSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.Apis.Api
  alias Airbyte.Source.GoogleAnalytics.Helpers

  def run(%ConnectorSpecification{} = spec) do
    with {:ok, token} <- spec |> Api.get_token(),
         true <- all_alive?(token, spec) do
      "All enabled APIs are alive" |> AirbyteConnectionStatus.succeeded()
    else
      false ->
        "Not all enabled APIs are alive" |> AirbyteConnectionStatus.failed()

      error ->
        "An error ocurred: #{inspect(error)}" |> AirbyteConnectionStatus.failed()
    end
  end

  defp all_alive?(%Goth.Token{} = token, %ConnectorSpecification{} = spec) do
    spec.connectionSpecification.apis
    |> Enum.map(&get_connection_status_async(token, &1))
    |> Enum.map(&Task.await/1)
    |> Enum.all?(fn result -> result == :ok end)
  end

  defp get_connection_status_async(%Goth.Token{} = token, result) do
    Task.async(fn ->
      Helpers.wrap_error(fn -> get_connection_status(token, result) end)
    end)
  end

  defp get_connection_status(%Goth.Token{} = token, {api, true}) do
    mod = Api.impl_for!(api)
    mod.connection_status(token)
  end

  defp get_connection_status(%Goth.Token{} = _, {api, _}) do
    mod = Api.impl_for!(api)

    "#{mod} is not enabled"
    |> AirbyteLogMessage.info()
    |> AirbyteMessage.dispatch()

    :ok
  end
end
