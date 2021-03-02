require_relative '../airbyte_logger.rb'

module MongodbConfiguredStream
  class Base
    attr_reader :processed_count, :configured_stream

    def initialize(configured_stream:, state:, client:)
      @configured_stream = configured_stream
      @state = state
      @client = client

      @processed_count = 0
    end

    def stream
      @stream ||= configured_stream['stream']
    end

    def stream_name
      @stream_name ||= configured_stream['stream']['name']
    end

    def sync_mode
      @sync_mode ||= configured_stream['sync_mode']
    end

    def compose_query
      {}
    end

    def valid?
      true
    end

    def after_item_processed(item)
      @processed_count += 1
    end

    def after_stream_processed
      AirbyteLogger.log("Stream #{stream_name} successfully processed!")
    end
  end
end
