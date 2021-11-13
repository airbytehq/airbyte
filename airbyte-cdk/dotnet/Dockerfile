# Build and publish cdk
FROM mcr.microsoft.com/dotnet/sdk:5.0

ENV NUGET_APIKEY="qz2jga8pl3dvn2akksyquwczaadggg4exypy3bhxy6w6x6"
ENV NUGET_SOURCE="https://api.nuget.org/v3/index.json"

ENV BUILD_VERSION="0.0.1"
ENV WORKDIR=/airbyte/build
WORKDIR $WORKDIR

COPY . ./

RUN dotnet test

WORKDIR $WORKDIR/Airbyte.Cdk
RUN dotnet build -c Release -p:Version=$BUILD_VERSION -o output
RUN dotnet nuget push ./output/Airbyte.Cdk.$BUILD_VERSION.nupkg --api-key $NUGET_APIKEY --source $NUGET_SOURCE
