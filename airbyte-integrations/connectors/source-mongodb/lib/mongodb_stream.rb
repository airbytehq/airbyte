require_relative './airbyte_protocol.rb'
require_relative './airbyte_logger.rb'

require_relative './mongodb_types_explorer.rb'

class MongodbStream
  DISCOVER_LIMIT = 10_000

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
      "source_defined_cursor" => false,
      "json_schema" => {
        "properties": @properties
      }
    }).to_dynamic
  end

  private


  def discover_property_type(property)
    MongodbTypesExplorer.run(collection: @collection, field: property) do |type|
      TYPES_MAPPING[type] || FALLBACK_TYPE
    end || FALLBACK_TYPE
  end

  def discover_properties
    map = "function() { for (var key in this) { emit(key, null); } }"
    reduce = "function(key, stuff) { return null; }"

    opts = {
      out: {inline: 1},
      raw: true,
    }

    view = Mongo::Collection::View.new(@collection, {}, limit: DISCOVER_LIMIT)
    props = view.map_reduce(map, reduce, opts).map do |obj|
      obj['_id']
    end

    props.each do |prop|
      @properties[prop] = { 'type' => discover_property_type(prop) }
      AirbyteLogger.log("  #{@collection.name}.#{prop} TYPE IS #{@properties[prop]['type']}")
    end
  end
end
