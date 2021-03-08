require_relative '../airbyte_logger.rb'

require_relative './full_refresh.rb'
require_relative './incremental.rb'

class MongodbConfiguredStream::Factory
  def self.build(configured_stream:, state:, client:)
    case configured_stream['sync_mode']
    when SyncMode::FullRefresh
      MongodbConfiguredStream::FullRefresh.new(configured_stream: configured_stream, state: state, client: client)
    when SyncMode::Incremental
      MongodbConfiguredStream::Incremental.new(configured_stream: configured_stream, state: state, client: client)
    else
      AirbyteLogger.log("Sync mode #{configured_stream['sync_mode']} is not supported!", Level::Fatal)
    end
  end
end
