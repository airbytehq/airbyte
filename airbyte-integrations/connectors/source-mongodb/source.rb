require 'optparse'
require 'mongo'
require 'slop'
require_relative './lib/mongodb_source'

# require 'byebug'

parsed = Slop.parse do |o|
  o.string '--config', 'Config file path'
  o.string '--catalog', 'Catalog file path'
  o.string '--state', 'State file path'
end

opts = parsed.to_hash.select { |_, value| value }

MongodbSource.new.public_send(parsed.arguments.first, **opts)
