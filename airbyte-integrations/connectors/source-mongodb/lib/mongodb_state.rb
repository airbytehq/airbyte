require_relative './airbyte_protocol.rb'
require_relative './airbyte_logger.rb'

require 'json'

class MongodbState

  def initialize(state_file:)
    @state = if state_file
               JSON.parse(File.read(state_file))
             else
               {}
             end
  end

  def get(stream_name:, cursor_field:)
    @state.dig(stream_name, cursor_field)
  end

  def set(stream_name:, cursor_field:, cursor:)
    @state[stream_name] ||= {}
    @state[stream_name][cursor_field] = cursor
  end

  def dump_state!
    json = @state.to_json

    AirbyteLogger.log("Saving state:\n#{JSON.pretty_generate(@state)}")

    File.write(state_file, @state.to_json)
  end
end
