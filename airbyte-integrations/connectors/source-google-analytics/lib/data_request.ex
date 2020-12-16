defmodule Airbyte.Source.GoogleAnalytics.DataRequest do
  @moduledoc """
  Airbyte Google Analytics Connection Specification
  """
  use TypedStruct

  require Logger

  alias GoogleApi.Analytics.V3.{Api, Connection, Model}

  @derive Jason.Encoder

  typedstruct do
    @typedoc "Airbyte Google Analytics Connection Specification"

    field(:profile_id, String.t(), enforce: true)
    field(:start_date, String.t(), enforce: true)
    field(:end_date, String.t(), enforce: true)
    field(:metrics, list(String.t()), enforce: true)
    field(:dimensions, list(String.t()), enforce: true)
    field(:start_index, Integer.t(), default: 1)
    field(:retries, Integer.t(), default: 0)
  end

  def serialize(%__MODULE__{} = request), do: request |> Jason.encode!()

  @spec query(Connection.t(), __MODULE__.t()) :: {:ok, GaData.t()} | {:error, String.t()}
  def query(conn, %__MODULE__{} = request) do
    Logger.info("DataRequest.get_data(): #{inspect(request)}")

    with {:ok, %Model.GaData{} = data} <- get_data(conn, request),
         {:next_request, next_request} <- next_request?(request, data),
         {:ok, %Model.GaData{} = data_next} <- query(conn, next_request) do
      all_data = %Model.GaData{data_next | rows: data.rows ++ data_next.rows}
      {:ok, all_data |> format_data()}
    else
      {:ok, data} -> {:ok, data}
      {:error, %Tesla.Env{} = error} -> maybe_retry?(conn, request, error)
      {:error, e} -> {:error, inspect(e)}
      e -> {:error, inspect(e)}
    end
  end

  defp next_request?(%__MODULE__{} = request, %Model.GaData{} = data) do
    case request.start_index + data.itemsPerPage <= data.totalResults do
      true ->
        next_index = request.start_index + data.itemsPerPage
        next_request = %__MODULE__{request | start_index: next_index, retries: 0}

        {:next_request, next_request}

      false ->
        {:ok, data}
    end
  end

  defp maybe_retry?(conn, %__MODULE__{} = request, %Tesla.Env{} = error) do
    with {:ok, body} <- Jason.decode(error.body, keys: :atoms) do
      case should_retry(%{status: error.status, body: body, retries: request.retries}) do
        true ->
          request |> backoff()
          query(conn, %__MODULE__{request | retries: request.retries + 1})

        false ->
          Logger.error("Not retrying anymore: #{inspect(body)}")
          {:error, body.error.message}
      end
    end
  end

  defp get_data(conn, %__MODULE__{} = request) do
    Api.Data.analytics_data_ga_get(
      conn,
      "ga:#{request.profile_id}",
      request.start_date,
      request.end_date,
      request.metrics |> Enum.join(","),
      dimensions: request.dimensions |> Enum.join(","),
      "start-index": request.start_index
    )
  end

  defp format_data(%Model.GaData{columnHeaders: headers, rows: rows}) do
    parsers = headers |> Enum.map(fn header -> {header.name, header_parser(header)} end)
    rows |> Enum.map(&format_row(&1, parsers)) |> IO.inspect()
  end

  defp format_row(row, parsers) do
    row
    |> Stream.zip(parsers)
    |> Stream.map(fn {value, {name, fun}} -> ["#{name}": fun.(value)] end)
    |> Stream.transform([], fn item, acc -> {item, acc ++ item} end)
    |> Enum.into(%{})
  end

  defp header_parser(%Model.GaDataColumnHeaders{dataType: "CURRENCY"}), do: &String.to_float/1
  defp header_parser(%Model.GaDataColumnHeaders{dataType: "FLOAT"}), do: &String.to_float/1
  defp header_parser(%Model.GaDataColumnHeaders{dataType: "INTEGER"}), do: &String.to_integer/1
  defp header_parser(%Model.GaDataColumnHeaders{dataType: "PERCENT"}), do: &String.to_float/1
  defp header_parser(%Model.GaDataColumnHeaders{dataType: "STRING"}), do: &Function.identity/1
  defp header_parser(%Model.GaDataColumnHeaders{dataType: "TIME"}), do: &String.to_float/1

  defp header_parser(%Model.GaDataColumnHeaders{dataType: type}) do
    Logger.warn("Unrecognized type: #{type}")
    &Function.identity/1
  end

  @retryable_errors ["userRateLimitExceeded", "rateLimitExceeded", "quotaExceeded"]

  defp should_retry(res),
    do: res.retries < 3 and res.status == 403 and is_retryable_403(res)

  defp is_retryable_403(res) do
    retryable_errors = @retryable_errors |> MapSet.new()
    error_reasons = res.body |> get_error_reasons() |> MapSet.new()

    MapSet.intersection(retryable_errors, error_reasons)
    |> MapSet.size()
    |> Kernel.>(0)
  end

  defp get_error_reasons(%{error: %{errors: errors}}),
    do: errors |> Enum.map(fn %{reason: reason} -> reason end)

  defp get_error_reasons(_), do: []

  defp backoff(%__MODULE__{retries: retries}) do
    random_milliseconds = 1000 |> :rand.uniform()
    maximum_backoff = 64 * 1000
    delay = :math.pow(2, retries) + random_milliseconds

    sleep = delay |> min(maximum_backoff) |> Kernel.trunc()

    Logger.debug("Retry \##{retries}, sleeping for #{sleep}ms")
    sleep |> Process.sleep()
  end
end
