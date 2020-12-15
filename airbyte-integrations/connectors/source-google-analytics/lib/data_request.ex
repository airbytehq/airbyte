defmodule Airbyte.Source.GoogleAnalytics.DataRequest do
  @moduledoc """
  Airbyte Google Analytics Connection Specification
  """
  use TypedStruct

  require Logger

  alias GoogleApi.Analytics.V3.{Api, Model}

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

  def query(conn, %__MODULE__{} = request) do
    Logger.info("DataRequest.get_data(): #{inspect(request)}")

    with {:ok, %Model.GaData{} = data} <- get_data(conn, request) do
      case request.start_index + data.itemsPerPage <= data.totalResults do
        true ->
          request = %__MODULE__{
            request
            | start_index: request.start_index + data.itemsPerPage,
              retries: 0
          }

          Logger.debug("Requesting #{request.start_index} of #{data.totalResults}")

          with {:ok, %Model.GaData{} = data_next} <- query(conn, request) do
            {:ok, %Model.GaData{data_next | rows: data.rows ++ data_next.rows}}
          else
            error ->
              Logger.error("Error: #{inspect(error)}")
              error
          end

        false ->
          {:ok, data}
      end
    end
  end

  defp get_data(conn, %__MODULE__{} = request) do
    result =
      Api.Data.analytics_data_ga_get(
        conn,
        "ga:#{request.profile_id}",
        request.start_date,
        request.end_date,
        request.metrics |> Enum.join(","),
        dimensions: request.dimensions |> Enum.join(","),
        "start-index": request.start_index
      )

    with {:error, %Tesla.Env{} = error} <- result,
         {:ok, body} <- Jason.decode(error.body) do
      case should_retry(%{status: error.status, body: body}) do
        true ->
          sleep = request |> calculate_backoff()

          Logger.debug("Retry \##{request.retries}: Sleeping for #{sleep}ms")
          sleep |> Process.sleep()

          get_data(conn, %__MODULE__{request | retries: request.retries + 1})

        false ->
          {:error, body.error.message}
      end
    end
  end

  @retryable_errors ["userRateLimitExceeded", "rateLimitExceeded", "quotaExceeded"]

  defp should_retry(res), do: res.status == 403 or is_retryable_403(res)

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

  defp calculate_backoff(%__MODULE__{retries: retries}) do
    random_milliseconds = 1000 |> :rand.uniform()
    maximum_backoff = 64 * 1000
    delay = :math.pow(2, retries) + random_milliseconds

    delay
    |> min(maximum_backoff)
    |> Kernel.trunc()
  end
end
