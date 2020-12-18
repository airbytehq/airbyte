defmodule Airbyte.Source.GoogleAnalytics.ConnectionSpecification do
  @moduledoc """
  Airbyte Google Analytics Connection Specification
  """
  use TypedStruct

  @derive Jason.Encoder

  typedstruct do
    @typedoc "Airbyte Google Analytics Connection Specification"

    field(:service_account_key, String.t())
    field(:reports, String.t())
  end
end
