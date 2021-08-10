require_relative './airbyte_protocol.rb'

require_relative './mongodb_stream.rb'

class MongodbTypesExplorer
  EXPLORE_LIMIT = 1_000

  @@cache = {}

  def self.run(collection:, field:, limit: EXPLORE_LIMIT, &type_mapping_block)
    determine_field_types_for_collection(collection: collection, limit: limit, &type_mapping_block)

    @@cache[collection.name][field]
  end

  private

  def self.determine_field_types_for_collection(collection:, limit:, &type_mapping_block)
    return if @@cache[collection.name]

    airbyte_types = {}

    collection.find.limit(limit).each do |item|
      item.each_pair do |key, value|
        mapped_value = type_mapping_block[value.class]

        airbyte_types[key] ||= Set[]
        airbyte_types[key].add(mapped_value)
      end
    end

    @@cache[collection.name] = {}
    airbyte_types.each_pair do |field, types|
      # Has one specific type
      if types.count == 1
        @@cache[collection.name][field] = types.first
      end
    end
  end
end
