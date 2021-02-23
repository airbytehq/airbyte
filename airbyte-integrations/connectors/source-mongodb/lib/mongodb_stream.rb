require_relative './airbyte_protocol.rb'

class MongodbStream
  PROPERTIES_DISCOVERY_LIMIT = 10_000
  TYPE_ANY = 'ANY_TYPE'
  TYPE_GROUPS = {
    simple: 'SIMPLE_TYPE_GROUP',
    complex: 'COMPLEX_TYPE_GROUP',
  }

  AIRBYTE_TYPES = {
    boolean: 'boolean',
    number: 'number',
    integer: 'integer',
    string: 'string',
    object: 'object',
    array: 'array',
  }

  TYPES_MAPPING = {
    Float => AIRBYTE_TYPES[:number],
    Integer => AIRBYTE_TYPES[:integer],
    String => AIRBYTE_TYPES[:string],
    DateTime => AIRBYTE_TYPES[:string],
    TrueClass => AIRBYTE_TYPES[:boolean],
    FalseClass => AIRBYTE_TYPES[:boolean],
    Array => AIRBYTE_TYPES[:array],
    Hash => AIRBYTE_TYPES[:object],
  }
  FALLBACK_TYPE = AIRBYTE_TYPES[:string]

  def initialize(collection:)
    @collection = collection
    @property_types = {}
    @properties = {}
  end

  def discover
    discover_property_types
    discover_properties

    AirbyteStream.from_dynamic!({
      "name" => @collection.name,
      "supported_sync_modes" => [SyncMode::FullRefresh],
      "json_schema" => {
        "properties": @properties
      }
    }).to_dynamic
  end

  private


  def discover_property_types
    @collection.find.limit(PROPERTIES_DISCOVERY_LIMIT).each do |item|
      item.each_pair do |key, value|
        @property_types[key] ||= Set[]
        @property_types[key].add value.class
      end
    end
  end

  def discover_properties
    @property_types.each_pair do |key, types|
      airbyte_types = types.map do |type|
        # Skip nil classes. No impact on actual column type
        if type != NilClass
          map_type(type)
        end
      end.compact

      type = if airbyte_types.count == 1 # Can be mapped to specific type
               airbyte_types.first
             else
               FALLBACK_TYPE
             end

      @properties[key] = { 'type' => type }
    end
  end

  def map_type(ruby_type)
    airbyte_type = TYPES_MAPPING[ruby_type] || FALLBACK_TYPE
  end
end
