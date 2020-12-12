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

  def json_to_struct(path, to_struct) do
    with {:ok, contents} <- path |> File.read(),
         {:ok, decoded} <- contents |> Jason.decode(keys: :atoms) do
      struct(to_struct, decoded)
    else
      {:error, :enoent} -> raise "Could not find file: #{path}"
    end
  end
end
