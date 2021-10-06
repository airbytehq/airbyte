require_relative '../airbyte_logger.rb'

require_relative './base.rb'
require_relative '../mongodb_types_converter.rb'
require_relative '../mongodb_types_explorer.rb'

class MongodbConfiguredStream::Incremental < MongodbConfiguredStream::Base
  DATETIME_TYPES = [Date, Time, DateTime]
  CURSOR_TYPES = {
    datetime: 'DATETIME',
    integer: 'integer',
  }

  attr_reader :cursor_field_type

  def initialize(configured_stream:, state:, client:)
    super

    @cursor_field_type = determine_cursor_field_type
    AirbyteLogger.log("Cursor type was determined as: #{@cursor_field_type}")

    value = @state.get(stream_name: stream_name, cursor_field: cursor_field)
    @cursor = value && convert_cursor(value)
  end

  def cursor_field
    @cursor_field ||= configured_stream['cursor_field']&.first
  end

  def compose_query
    if @cursor
      {
        cursor_field => {
          "$gt": @cursor
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

    if item[cursor_field]
      converted_cursor = convert_cursor(item[cursor_field])
      if !@cursor || converted_cursor && converted_cursor > @cursor
        @cursor = converted_cursor
      end
    else
      AirbyteLogger.log("Cursor is empty! Incremental sync results might be unpredictable! Item: #{item}", Level::Fatal)
    end
  end

  def after_stream_processed
    super

    @state.set(stream_name: stream_name, cursor_field: cursor_field, cursor: @cursor)
    @state.dump_state!
  end

  private

  def determine_cursor_field_type
    MongodbTypesExplorer.run(collection: @client[stream_name], field: cursor_field) do |type|
      if DATETIME_TYPES.include?(type)
        CURSOR_TYPES[:datetime]
      else
        CURSOR_TYPES[:integer]
      end
    end
  end

  def convert_cursor(value)
    if cursor_field_type == CURSOR_TYPES[:datetime]
      Time.parse(value)
    elsif cursor_field_type == CURSOR_TYPES[:integer]
      value.to_i
    else
      AirbyteLogger.log("Cursor type #{cursor_field_type} is not supported!", Level::Fatal)
    end
  end

end
