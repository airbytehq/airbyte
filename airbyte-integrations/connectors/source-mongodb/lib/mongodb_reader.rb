require_relative './airbyte_protocol.rb'
require_relative './mongodb_logger.rb'
require_relative './mongodb_stream.rb'

class MongodbReader
  BATCH_SIZE = 10_000
  LOG_BATCH_SIZE = 10_000

  def initialize(client:, catalog:, state:)
    @client = client
    @catalog = catalog
    @state = state
  end

  def read
    @catalog['streams'].each do |stream_object|
      stream = stream_object['stream']
      MongodbLogger.log("Reading stream #{stream['name']} in #{stream['sync_mode']} mode")
      read_stream(stream)
    end
  end

  private

  def read_stream(stream)
    collection = @client[stream['name']]

    projection_config = stream['json_schema']['properties'].keys.each_with_object({}) do |key, obj|
      obj[key] = 1
    end

    full_count = collection.count
    processed_count = 0

    collection.find.projection(projection_config).batch_size(BATCH_SIZE).each do |item|
      item.each_pair do |key, value|
        item[key] = convert_value_to_type(value, stream['json_schema']['properties'][key]['type'])
      end

      record = AirbyteRecordMessage.from_dynamic!({
        "data" => item,
        "emitted_at" => Time.now.to_i * 1000,
        "stream" => stream['name'],
      })

      message =  AirbyteMessage.from_dynamic!({
        'type' => Type::Record,
        'record' => record.to_dynamic,
      })

      puts message.to_json

      processed_count += 1
      if processed_count % LOG_BATCH_SIZE == 0
        MongodbLogger.log("[#{processed_count}/#{full_count}}] Reading stream #{stream['name']} is in progress")
      end
    end

    MongodbLogger.log("Stream #{stream['name']} successfully processed!")
  end

  def convert_value_to_type(value, type)
    case type
    when MongodbStream::AIRBYTE_TYPES[:boolean]
      !!value
    when MongodbStream::AIRBYTE_TYPES[:number]
      value.to_f
    when MongodbStream::AIRBYTE_TYPES[:integer]
      value.to_i
    when MongodbStream::AIRBYTE_TYPES[:string]
      value.to_s
    when MongodbStream::AIRBYTE_TYPES[:object]
      value.is_a?(Hash) ? value : { 'value' => value.to_s }
    when MongodbStream::AIRBYTE_TYPES[:array]
      value.is_a?(Array) ? value : [ value.to_s ]
    else
      value.to_s
    end
  end
end
