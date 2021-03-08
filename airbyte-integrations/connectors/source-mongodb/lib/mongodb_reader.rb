require_relative './airbyte_protocol.rb'
require_relative './airbyte_logger.rb'

require_relative './mongodb_stream.rb'
require_relative './mongodb_types_converter.rb'
require_relative './mongodb_configured_stream/factory.rb'

class MongodbReader
  BATCH_SIZE = 10_000
  LOG_BATCH_SIZE = 10_000

  def initialize(client:, catalog:, state:)
    @client = client
    @catalog = catalog
    @state = state
  end

  def read
    @catalog['streams'].each do |configured_stream|
      wrapper = MongodbConfiguredStream::Factory.build(configured_stream: configured_stream, state: @state, client: @client)

      AirbyteLogger.log("Reading stream #{wrapper.stream_name} in #{wrapper.sync_mode} mode")

      if wrapper.valid?
        read_configured_stream(wrapper)
      end
    end
  end

  private

  def read_configured_stream(wrapper)
    collection = @client[wrapper.stream_name]

    projection_config = wrapper.stream['json_schema']['properties'].keys.each_with_object({}) do |key, obj|
      obj[key] = 1
    end

    full_count = collection.count

    collection.find(wrapper.compose_query).projection(projection_config).batch_size(BATCH_SIZE).each do |item|
      item.each_pair do |key, value|
        item[key] = MongodbTypesConverter.convert_value_to_type(value, wrapper.stream['json_schema']['properties'][key]['type'])
      end

      record = AirbyteRecordMessage.from_dynamic!({
        "data" => item,
        "emitted_at" => Time.now.to_i * 1000,
        "stream" => wrapper.stream_name,
      })

      message =  AirbyteMessage.from_dynamic!({
        'type' => Type::Record,
        'record' => record.to_dynamic,
      })

      puts message.to_json

      wrapper.after_item_processed(item)

      if wrapper.processed_count % LOG_BATCH_SIZE == 0
        AirbyteLogger.log("[#{wrapper.processed_count}/#{full_count}}] Reading stream #{wrapper.stream_name} is in progress")
      end
    end

    wrapper.after_stream_processed
  end
end
