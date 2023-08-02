require_relative './airbyte_protocol.rb'

require_relative './mongodb_stream.rb'

class MongodbTypesConverter
  def self.convert_value_to_type(value, type)
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
