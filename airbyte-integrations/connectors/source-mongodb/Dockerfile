FROM ruby:3.0-alpine

RUN apk update
RUN apk add --update build-base libffi-dev

WORKDIR /airbyte

COPY . ./

RUN gem install bundler
RUN bundle install

ENV AIRBYTE_ENTRYPOINT "ruby /airbyte/source.rb"
ENTRYPOINT ["ruby", "/airbyte/source.rb"]

LABEL io.airbyte.name=airbyte/source-mongodb
LABEL io.airbyte.version=0.3.3
