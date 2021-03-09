# The file was generated in several steps.
#
# 1. Convert airbyte_protocol.yaml to JSON
# 2. Use https://app.quicktype.io/?l=ruby to generate code. Parameters:
#   Type strictness: Coercible
#   Plain types only: Disabled
# 3. Fix module `Types` according to https://dry-rb.org/gems/dry-types/master/built-in-types/
# 4. Replace all instance variable calls to just method calls (remove all  characters)
# 4. Add `.compact` call to resulting object in every `to_dynamic` method
#
#
#
# This code may look unusually verbose for Ruby (and it is), but
# it performs some subtle and complex validation of JSON data.
#
# To parse this JSON, add 'dry-struct' and 'dry-types' gems, then do:
#
#   airbyte = Airbyte.from_json! "{…}"
#   puts airbyte.configured_airbyte_catalog&.streams.first.stream.supported_sync_modes&.first
#
# If from_json! succeeds, the value returned matches the schema.

require 'json'
require 'dry-types'
require 'dry-struct'

module Types
  include Dry::Types()

  Int      = Coercible::Integer
  Bool     = Strict::Bool
  Hash     = Coercible::Hash
  String   = Coercible::String
  Type     = Coercible::String.enum("CATALOG", "CONNECTION_STATUS", "LOG", "RECORD", "SPEC", "STATE")
  SyncMode = Coercible::String.enum("full_refresh", "incremental")
  Status   = Coercible::String.enum("FAILED", "SUCCEEDED")
  Level    = Coercible::String.enum("DEBUG", "ERROR", "FATAL", "INFO", "TRACE", "WARN")
end

# Message type
module Type
  Catalog          = "CATALOG"
  ConnectionStatus = "CONNECTION_STATUS"
  Log              = "LOG"
  Record           = "RECORD"
  Spec             = "SPEC"
  State            = "STATE"
end

module SyncMode
  FullRefresh = "full_refresh"
  Incremental = "incremental"
end

class AirbyteStream < Dry::Struct

  # Path to the field that will be used to determine if a record is new or modified since the
  # last sync. If not provided by the source, the end user will have to specify the
  # comparable themselves.
  attribute :default_cursor_field, Types.Array(Types::String).optional

  # Stream schema using Json Schema specs.
  attribute :json_schema, Types::Hash.meta(of: Types::Any)

  # Stream's name.
  attribute :airbyte_stream_name, Types::String

  # If the source defines the cursor field, then it does any other cursor field inputs will
  # be ignored. If it does not either the user_provided one is used or as a backup the
  # default one is used.
  attribute :source_defined_cursor, Types::Bool.optional

  attribute :supported_sync_modes, Types.Array(Types::SyncMode).optional

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      default_cursor_field:  d["default_cursor_field"],
      json_schema:           Types::Hash[d.fetch("json_schema")].map { |k, v| [k, Types::Any[v]] }.to_h,
      airbyte_stream_name:   d.fetch("name"),
      source_defined_cursor: d["source_defined_cursor"],
      supported_sync_modes:  d["supported_sync_modes"],
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "default_cursor_field"  => default_cursor_field,
      "json_schema"           => json_schema,
      "name"                  => airbyte_stream_name,
      "source_defined_cursor" => source_defined_cursor,
      "supported_sync_modes"  => supported_sync_modes,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

# log message: any kind of logging you want the platform to know about.
#
# Airbyte stream schema catalog
class AirbyteCatalog < Dry::Struct
  attribute :streams, Types.Array(AirbyteStream)

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      streams: d.fetch("streams").map { |x| AirbyteStream.from_dynamic!(x) },
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "streams" => streams.map { |x| x.to_dynamic },
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

module Status
  Failed    = "FAILED"
  Succeeded = "SUCCEEDED"
end

# Airbyte connection status
class AirbyteConnectionStatus < Dry::Struct
  attribute :message, Types::String.optional
  attribute :status,  Types::Status

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      message: d["message"],
      status:  d.fetch("status"),
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "message" => message,
      "status"  => status,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

# the type of logging
module Level
  Debug = "DEBUG"
  Error = "ERROR"
  Fatal = "FATAL"
  Info  = "INFO"
  Trace = "TRACE"
  Warn  = "WARN"
end

# log message: any kind of logging you want the platform to know about.
class AirbyteLogMessage < Dry::Struct

  # the type of logging
  attribute :level, Types::Level

  # the log message
  attribute :message, Types::String

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      level:   d.fetch("level"),
      message: d.fetch("message"),
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "level"   => level,
      "message" => message,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

# record message: the record
class AirbyteRecordMessage < Dry::Struct

  # the record data
  attribute :data, Types::Hash.meta(of: Types::Any)

  # when the data was emitted from the source. epoch in millisecond.
  attribute :emitted_at, Types::Int

  # the name of the stream for this record
  attribute :stream, Types::String

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      data:       Types::Hash[d.fetch("data")].map { |k, v| [k, Types::Any[v]] }.to_h,
      emitted_at: d.fetch("emitted_at"),
      stream:     d.fetch("stream"),
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "data"       => data,
      "emitted_at" => emitted_at,
      "stream"     => stream,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

# Specification of a connector (source/destination)
class ConnectorSpecification < Dry::Struct
  attribute :changelog_url, Types::String.optional

  # ConnectorDefinition specific blob. Must be a valid JSON string.
  attribute :connection_specification, Types::Hash.meta(of: Types::Any)

  attribute :documentation_url, Types::String.optional

  # If the connector supports incremental mode or not.
  attribute :supports_incremental, Types::Bool.optional

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      changelog_url:            d["changelogUrl"],
      connection_specification: Types::Hash[d.fetch("connectionSpecification")].map { |k, v| [k, Types::Any[v]] }.to_h,
      documentation_url:        d["documentationUrl"],
      supports_incremental:     d["supportsIncremental"],
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "changelogUrl"            => changelog_url,
      "connectionSpecification" => connection_specification,
      "documentationUrl"        => documentation_url,
      "supportsIncremental"     => supports_incremental,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

# schema message: the state. Must be the last message produced. The platform uses this
# information
class AirbyteStateMessage < Dry::Struct

  # the state data
  attribute :data, Types::Hash.meta(of: Types::Any)

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      data: Types::Hash[d.fetch("data")].map { |k, v| [k, Types::Any[v]] }.to_h,
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "data" => data,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

class AirbyteMessage < Dry::Struct

  # log message: any kind of logging you want the platform to know about.
  attribute :catalog, AirbyteCatalog.optional

  attribute :connection_status, AirbyteConnectionStatus.optional

  # log message: any kind of logging you want the platform to know about.
  attribute :log, AirbyteLogMessage.optional

  # record message: the record
  attribute :record, AirbyteRecordMessage.optional

  attribute :spec, ConnectorSpecification.optional

  # schema message: the state. Must be the last message produced. The platform uses this
  # information
  attribute :state, AirbyteStateMessage.optional

  # Message type
  attribute :airbyte_message_type, Types::Type

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      catalog:              d["catalog"] ? AirbyteCatalog.from_dynamic!(d["catalog"]) : nil,
      connection_status:    d["connectionStatus"] ? AirbyteConnectionStatus.from_dynamic!(d["connectionStatus"]) : nil,
      log:                  d["log"] ? AirbyteLogMessage.from_dynamic!(d["log"]) : nil,
      record:               d["record"] ? AirbyteRecordMessage.from_dynamic!(d["record"]) : nil,
      spec:                 d["spec"] ? ConnectorSpecification.from_dynamic!(d["spec"]) : nil,
      state:                d["state"] ? AirbyteStateMessage.from_dynamic!(d["state"]) : nil,
      airbyte_message_type: d.fetch("type"),
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "catalog"          => catalog&.to_dynamic,
      "connectionStatus" => connection_status&.to_dynamic,
      "log"              => log&.to_dynamic,
      "record"           => record&.to_dynamic,
      "spec"             => spec&.to_dynamic,
      "state"            => state&.to_dynamic,
      "type"             => airbyte_message_type,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

class ConfiguredAirbyteStream < Dry::Struct

  # Path to the field that will be used to determine if a record is new or modified since the
  # last sync. This field is REQUIRED if `sync_mode` is `incremental`. Otherwise it is
  # ignored.
  attribute :cursor_field, Types.Array(Types::String).optional

  attribute :stream,    AirbyteStream
  attribute :sync_mode, Types::SyncMode.optional

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      cursor_field: d["cursor_field"],
      stream:       AirbyteStream.from_dynamic!(d.fetch("stream")),
      sync_mode:    d["sync_mode"],
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "cursor_field" => cursor_field,
      "stream"       => stream.to_dynamic,
      "sync_mode"    => sync_mode,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

# Airbyte stream schema catalog
class ConfiguredAirbyteCatalog < Dry::Struct
  attribute :streams, Types.Array(ConfiguredAirbyteStream)

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      streams: d.fetch("streams").map { |x| ConfiguredAirbyteStream.from_dynamic!(x) },
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "streams" => streams.map { |x| x.to_dynamic },
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end

# AirbyteProtocol structs
class Airbyte < Dry::Struct
  attribute :airbyte_message,            AirbyteMessage.optional
  attribute :configured_airbyte_catalog, ConfiguredAirbyteCatalog.optional

  def self.from_dynamic!(d)
    d = Types::Hash[d]
    new(
      airbyte_message:            d["airbyte_message"] ? AirbyteMessage.from_dynamic!(d["airbyte_message"]) : nil,
      configured_airbyte_catalog: d["configured_airbyte_catalog"] ? ConfiguredAirbyteCatalog.from_dynamic!(d["configured_airbyte_catalog"]) : nil,
    )
  end

  def self.from_json!(json)
    from_dynamic!(JSON.parse(json))
  end

  def to_dynamic
    {
      "airbyte_message"            => airbyte_message&.to_dynamic,
      "configured_airbyte_catalog" => configured_airbyte_catalog&.to_dynamic,
    }.compact
  end

  def to_json(options = nil)
    JSON.generate(to_dynamic, options)
  end
end
