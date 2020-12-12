defmodule Airbyte.Source.GoogleAnalytics.Apis.Api do
  alias Airbyte.Protocol.{
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStream,
    ConnectorSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.Apis

  @implementations [
    admin: Apis.Admin,
    analytics: Apis.Analytics,
    data: Apis.Data,
    reporting: Apis.Reporting
  ]

  @callback connection_status(Goth.Token.t()) :: :ok | {:error, String.t()}
  @callback discover(ConnectorSpecification.t()) :: list(AirbyteStream.t())

  def impl(), do: @implementations
  def impl_for!(name), do: impl() |> Keyword.fetch!(name)

  def get_token(%ConnectorSpecification{connectionSpecification: %{serviceAccountKeyPath: path}}) do
    with {:ok, json} <- path |> File.read!() |> Poison.decode(),
         account <- json["client_email"],
         :ok <- Goth.Config.add_config(json) do
      scope = "https://www.googleapis.com/auth/analytics.readonly"
      Goth.Token.for_scope({account, scope})
    end
  end

  def connection_status(module, :ok) do
    "#{module} is OK"
    |> AirbyteLogMessage.info()
    |> AirbyteMessage.dispatch()

    :ok
  end

  def connection_status(module, {:error, %Tesla.Env{body: body}}) do
    parse_api_error(module, body)
    |> AirbyteLogMessage.error()
    |> AirbyteMessage.dispatch()

    :error
  end

  def connection_status(module, {:error, message}) do
    "#{module} failed with: #{message}"
    |> AirbyteLogMessage.error()
    |> AirbyteMessage.dispatch()

    :error
  end

  def connection_status(module, _) do
    "#{module} failed with: unknown error"
    |> AirbyteLogMessage.error()
    |> AirbyteMessage.dispatch()

    :error
  end

  defp parse_api_error(module, body) do
    with {:ok, body} <- Jason.decode(body) do
      "#{module} failed with code #{body.error.code}: #{body.error.message}"
    else
      _ -> "#{module} failed with: #{body}"
    end
  end
end
