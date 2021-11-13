# Build and test implementation
FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build

ENV WORKDIR=/airbyte/build
WORKDIR $WORKDIR

COPY . ./
COPY NuGet.Config /root/.nuget/NuGet/

RUN dotnet test
RUN dotnet build -c Release -o output

# Run implementation
FROM mcr.microsoft.com/dotnet/runtime:5.0 AS runtime

ENV WORKDIR=/airbyte/integration_code
WORKDIR $WORKDIR

COPY --from=build /airbyte/build/output .

ENV AIRBYTE_IMPL_PATH="/airbyte/integration_code/source_exchange_rates.dll"
ENV AIRBYTE_IMPL_MODULE="ExchangeRates"
ENTRYPOINT ["dotnet", "/airbyte/integration_code/source_exchange_rates.dll", "read", "--command"]

LABEL io.airbyte.version=0.0.1
LABEL io.airbyte.name=airbyte/source-exchange-rates-free