defmodule Airbyte.Source.GoogleAnalytics.Cli do
  @moduledoc """
  Documentation for `AirbyteSourceGoogleAnalytics`.
  """

  alias Airbyte.Protocol.{ConfiguredAirbyteCatalog, ConnectorSpecification}
  alias Airbyte.Source.GoogleAnalytics
  alias Airbyte.Source.GoogleAnalytics.Helpers

  # CLI entrypoint
  def main(args) do
    # Helpers.wrap_error(fn -> run(args) end)
    run(args)
  end

  defp run([]), do: raise("No command specified")

  defp run([command | args]) do
    with cmd <- command |> String.to_atom(),
         options <- parse(cmd, args),
         :ok <- run(cmd, options) do
    else
      e -> raise e
    end
  end

  defp run(:check, args), do: GoogleAnalytics.check(args)
  defp run(:discover, args), do: GoogleAnalytics.discover(args)
  defp run(:read, args), do: GoogleAnalytics.read(args)
  defp run(:spec, _), do: GoogleAnalytics.spec()
  defp run(command, _), do: raise("Unknown command: #{command}")

  defp parse(:check, args), do: parse_config(args)
  defp parse(:discover, args), do: parse_config(args)
  defp parse(:read, args), do: [config: parse_config(args), catalog: parse_catalog(args)]
  defp parse(_, _), do: nil

  defp parse_config(args) do
    [config: config] = parse_options(args, config: :string)
    config |> ConnectorSpecification.from_file()
  end

  defp parse_catalog(args) do
    [catalog: catalog] = parse_options(args, catalog: :string)
    catalog |> ConfiguredAirbyteCatalog.from_file()
  end

  defp parse_options(args, options) do
    {opts, _, _} = OptionParser.parse(args, strict: options)
    opts
  end
end
