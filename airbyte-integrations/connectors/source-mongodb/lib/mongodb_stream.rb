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
    @properties = {}
  end

  def discover
    discover_properties

    AirbyteStream.from_dynamic!({
      "name" => @collection.name,
      "supported_sync_modes" => [SyncMode::FullRefresh, SyncMode::Incremental],
      "json_schema" => {
        "properties": @properties
      }
    }).to_dynamic
  end

  private


  def discover_property_type(property)
    airbyte_types = Set[]

    @collection.find(property => { "$nin": [nil] }).limit(PROPERTIES_DISCOVERY_LIMIT).each do |item|
      airbyte_types.add(map_type(item[property].class))
    end

    if airbyte_types.count == 1 # Can be mapped to specific type
      airbyte_types.first
    else
      FALLBACK_TYPE
    end
  end

  def discover_properties
    map = "function() { for (var key in this) { emit(key, null); } }"
    reduce = "function(key, stuff) { return null; }"

    opts = {
      out: {inline: 1},
      raw: true,
    }

    view = Mongo::Collection::View.new(@collection)
    props = view.map_reduce(map, reduce, opts).map do |obj|
      obj['_id']
    end

    props.each do |prop|
      @properties[prop] = { 'type' => discover_property_type(prop) }
    end
  end

  def map_type(ruby_type)
    airbyte_type = TYPES_MAPPING[ruby_type] || FALLBACK_TYPE
  end
end
