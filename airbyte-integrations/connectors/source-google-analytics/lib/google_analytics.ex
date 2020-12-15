defmodule Airbyte.Source.GoogleAnalytics.GoogleAnalytics do
  alias Airbyte.Source.GoogleAnalytics.ConnectionSpecification
  alias GoogleApi.Analytics.V3.Connection

  def connection(%ConnectionSpecification{} = spec) do
    with {:ok, %Goth.Token{token: token}} <- spec |> get_token() do
      {:ok, token |> Connection.new()}
    end
  end

  def get_token(%ConnectionSpecification{service_account_key: path}) do
    with {:ok, json} <- path |> File.read!() |> Poison.decode(),
         account <- json["client_email"],
         :ok <- Goth.Config.add_config(json) do
      scope = "https://www.googleapis.com/auth/analytics.readonly"
      Goth.Token.for_scope({account, scope})
    end
  end

  def get_error_message({:error, %Tesla.Env{body: body}}), do: parse_api_error(body)

  def get_error_message({:error, msg}), do: "Connection failed with: #{msg}"
  def get_error_message(_), do: "Connection failed with: unknown error"

  defp parse_api_error(body) do
    case Jason.decode(body) do
      {:ok, body} ->
        "Connection failed with code #{body.error.code}: #{body.error.message}"

      _ ->
        "Connection failed with: #{body}"
    end
  end
end
