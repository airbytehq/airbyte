defmodule Airbyte.Source.GoogleAnalytics.Commands.Discover do
  alias Airbyte.Protocol.{
    AirbyteCatalog,
    AirbyteStream
  }

  alias Airbyte.Source.GoogleAnalytics.{
    ConnectionSpecification,
    GoogleAnalytics,
    Streams
  }

  alias GoogleApi.Analytics.V3.Api.{Management, Metadata}
  alias GoogleApi.Analytics.V3.Connection
  alias GoogleApi.Analytics.V3.Model.{AccountSummary, WebPropertySummary, Column, Columns}

  def run(%ConnectionSpecification{} = spec) do
    # {:ok, conn} = GoogleAnalytics.connection(spec)

    # Management.analytics_management_account_summaries_list(conn)
    # |> IO.inspect()
    # get_custom_fields(conn)

    streams = [
      Streams.Accounts.stream(),
      Streams.Profiles.stream(),
      Streams.WebProperties.stream()
    ]

    catalog = AirbyteCatalog.create(streams)

    {:ok, catalog}
  end

  @unsupported_fields [
    # "ga:customVarValueXX",
    # "ga:customVarNameXX",
    # "ga:calcMetric_<NAME>"
  ]

  defp get_standard_fields(conn) do
    {:ok, columns} = Metadata.analytics_metadata_columns_list(conn, "ga")
    columns.items |> Enum.filter(&filter_unsupported_fields/1)
  end

  defp filter_unsupported_fields(%Column{id: id}) do
    Enum.member?(@unsupported_fields, id)
  end

  defp get_custom_fields(conn) do
    get_custom_dimensions(conn) ++ get_custom_metrics(conn)
  end

  defp get_custom_dimensions(conn) do
    conn
    |> accounts()
    |> Enum.map(&get_account_custom_dimensions(conn, &1))
    |> List.flatten()
  end

  defp get_account_custom_dimensions(conn, %AccountSummary{} = account) do
    account.webProperties |> Enum.map(&get_web_property_custom_dimensions(conn, account, &1))
  end

  defp get_web_property_custom_dimensions(
         conn,
         %AccountSummary{} = account,
         %WebPropertySummary{} = property
       ) do
    with {:ok, custom_dimensions} <-
           Management.analytics_management_custom_dimensions_list(
             conn,
             account.id,
             property.id
           ) do
      custom_dimensions.items
    end
  end

  defp get_custom_metrics(conn) do
    conn
    |> accounts()
    |> Enum.map(&get_account_custom_metrics(conn, &1))
    |> List.flatten()
  end

  defp get_account_custom_metrics(conn, %AccountSummary{} = account) do
    IO.inspect(account)
    account.webProperties |> Enum.map(&get_web_property_custom_metrics(conn, account, &1))
  end

  defp get_web_property_custom_metrics(
         conn,
         %AccountSummary{} = account,
         %WebPropertySummary{} = property
       ) do
    with {:ok, custom_metrics} <-
           Management.analytics_management_custom_metrics_list(
             conn,
             account.id,
             property.id
           ) do
      custom_metrics.items
    end
  end

  defp accounts(conn) do
    with {:ok, summary} <- Management.analytics_management_account_summaries_list(conn) do
      summary.items
    end
  end
end
