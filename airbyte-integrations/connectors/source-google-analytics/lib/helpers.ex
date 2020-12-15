defmodule Airbyte.Source.GoogleAnalytics.Helpers do
  alias Airbyte.Protocol.{AirbyteLogMessage, AirbyteMessage}

  def wrap_error(fun) do
    try do
      fun.()
    rescue
      error -> error |> dispatch_error()
    catch
      :exit, error -> error |> dispatch_error()
      error -> error |> dispatch_error()
    end
  end

  def dispatch_error(error) do
    error
    |> inspect()
    |> AirbyteLogMessage.fatal()
    |> AirbyteMessage.dispatch()

    :error
  end
end
