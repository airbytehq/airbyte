require_relative '../airbyte_logger.rb'

require_relative './base.rb'
require_relative '../mongodb_types_converter.rb'

class MongodbConfiguredStream::Incremental < MongodbConfiguredStream::Base
  def new(configured_stream:, state:)
    super

    value = @state.get(stream_name: stream_name, cursor_field: cursor_field)
    @cursor =  MongodbTypesConverter.convert_value_to_type(value, stream['json_schema']['properties'][cursor_field]['type'])
  end

  def cursor_field
    @cursor_field ||= configured_stream['cursor_field']&.first
  end

  def compose_query
    if converted_cursor
      {
        cursor_field => {
          "$gte": converted_cursor
        }
      }
    else
      {}
    end
  end

  def valid?
    if configured_stream['cursor_field'].count != 1
      AirbyteLogger.log("Stream #{stream_name} has invalid configuration. Cursor field #{wrapper['cursor_field']} configuration is invalid. Should contain exactly one document property name.", Level::Fatal)
      return false
    end

    true
  end

  def after_item_processed(item)
    super

    if !@cursor || item[cursor_field] && item[cursor_field] > @cursor
      @cursor = item[cursor_field]
    end
  end

  def after_stream_processed
    super

    @state.set(stream_name: stream_name, cursor_field: cursor_field, cursor: @cursor)
    @state.dump_state!
  end
end
