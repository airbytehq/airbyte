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

    AirbyteLogger.log("Initialized with state:\n#{JSON.pretty_generate(@state)}")
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

    asm = AirbyteStateMessage.from_dynamic!({
      'data' => @state,
    })

    message =  AirbyteMessage.from_dynamic!({
      'type' => Type::State,
      'state' => asm.to_dynamic,
    })

    puts message.to_json
  end
end
