require_relative './airbyte_protocol.rb'

require_relative './mongodb_stream.rb'

class MongodbTypesExplorer
  EXPLORE_LIMIT = 1_000

  attr_reader :field_type

  def initialize(collection:, field:, limit: EXPLORE_LIMIT, &type_mapping_block)
    @collection = collection
    @field = field
    @limit = limit
    @type_mapping_block = type_mapping_block

    @field_type = determine_field_type
  end

  private

  def determine_field_type
    airbyte_types = Set[]

    @collection.find(@field => { "$nin": [nil] }).limit(@limit).each do |item|
      mapped_value = @type_mapping_block[item[@field].class]
      airbyte_types.add(mapped_value)
    end

    # Has one specific type
    if airbyte_types.count == 1
      airbyte_types.first
    end
  end
end
