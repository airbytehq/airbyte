require_relative './airbyte_protocol.rb'

class AirbyteLogger
  def self.format_log(text, log_level=Level::Info)
    alm = AirbyteLogMessage.from_dynamic!({
      'level' => log_level,
      'message' => text
    })

    AirbyteMessage.from_dynamic!({
      'type' => Type::Log,
      'log' => alm.to_dynamic
    }).to_json
  end

  def self.logger_formatter
    proc { |severity, datetime, progname, msg|
      format_log("[#{datetime}] #{severity} : #{progname} | #{msg.dump}\n\n")
    }
  end

  def self.log(text, log_level=Level::Info)
    message = format_log(text, log_level=Level::Info)

    puts message
  end
end
