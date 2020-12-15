defmodule Airbyte.Source.GoogleAnalytics.Commands.Read do
  alias Airbyte.Protocol.{
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectionSpecification
  }

  alias Airbyte.Source.GoogleAnalytics.{
    ConnectionSpecification,
    Client,
    Streams
  }

  alias GoogleApi.Analytics.V3.Api.{Management, Metadata}

  alias GoogleApi.Analytics.V3.Model.{
    AccountSummary,
    WebPropertySummary,
    ProfileSummary
  }

  def run(
        config: %ConnectionSpecification{} = spec,
        catalog: %ConfiguredAirbyteCatalog{} = catalog,
        state: state
      ) do
    # stream =
    #   Stream.concat(
    #     static_streams(spec)
    #     catalog.streams |> process_stream(spec, &1, state)
    #   )
    #   |> Stream.filter()

    # stream = catalog.streams |> Stream.map(&process_stream(spec, &1, state))

    stream = static_streams(spec)

    # |> Stream.map(&Function.identity/1)

    {:ok, stream}
  end

  def process_stream(
        %ConnectionSpecification{} = spec,
        %ConfiguredAirbyteStream{} = stream,
        state
      ) do
    case stream.stream.name do
      "accounts" -> nil
      # "profiles" -> process_stream_profiles(spec)
      # "web_properties" -> process_stream_web_properties(spec)
      _ -> nil
    end
  end

  defp static_streams(%ConnectionSpecification{} = spec) do
    with {:ok, conn} <- Client.connection(spec),
         {:ok, summary} <- Management.analytics_management_account_summaries_list(conn) do
      summary.items |> Enum.map(&process_account/1) |> List.flatten()
    end
  end

  defp process_account(%AccountSummary{} = account) do
    record = Streams.Accounts.new(account) |> Streams.Accounts.record()
    properties = Enum.map(account.webProperties, &process_web_property(account, &1))

    [record] ++ properties
  end

  defp process_web_property(%AccountSummary{} = account, %WebPropertySummary{} = property) do
    record = Streams.WebProperties.new(account, property) |> Streams.WebProperties.record()
    profiles = Enum.map(property.profiles, &process_profile(account, property, &1))

    [record] ++ profiles
  end

  defp process_profile(
         %AccountSummary{} = account,
         %WebPropertySummary{} = property,
         %ProfileSummary{} = profile
       ) do
    Streams.Profiles.new(account, property, profile) |> Streams.Profiles.record()
  end
end
