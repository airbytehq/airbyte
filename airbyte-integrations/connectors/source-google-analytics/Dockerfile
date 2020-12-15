FROM elixir:1.11-alpine as builder

ARG MIX_ENV
ENV MIX_ENV=${MIX_ENV:-prod}

WORKDIR /app

ADD . .

# this is due to hackney being intalled as a git dependency
# remove when hackney 1.17 is released
RUN apk add --no-cache git

RUN mix local.hex --force && \
  mix local.rebar --force && \
  mix deps.get && \
  mix compile && \
  mix escript.build

FROM erlang:23-alpine

ARG MIX_ENV
ENV MIX_ENV=${MIX_ENV:-prod}

WORKDIR /app

RUN apk add --no-cache ca-certificates

COPY --from=builder /app/airbyte_source_google_analytics .

ENTRYPOINT ["/app/airbyte_source_google_analytics"]

LABEL io.airbyte.version=0.1.0
LABEL io.airbyte.name=airbyte/source-google-analytics
