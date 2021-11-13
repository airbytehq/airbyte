using System;
using Airbyte.Cdk.Models;
using Type = Airbyte.Cdk.Models.Type;

namespace Airbyte.Cdk
{
    public class AirbyteLogger
    {
        public void Log(Level level, string message)
        {
            var logrecord = new AirbyteLogMessage {Level = level, Message = message};
            var logmessage = new AirbyteMessage {Type = Type.LOG, Log = logrecord};
            AirbyteEntrypoint.ToConsole(logmessage);
        }

        public void Fatal(string message) => Log(Level.FATAL, message);

        public void Exception(Exception exception) => Log(Level.ERROR, $"{exception.Message}{Environment.NewLine}{exception.StackTrace}");

        public void Error(string message) => Log(Level.ERROR, message);

        public void Warn(string message) => Log(Level.WARN, message);

        public void Info(string message) => Log(Level.INFO, message);

        public void Debug(string message) => Log(Level.DEBUG, message);

        public void Trace(string message) => Log(Level.TRACE, message);
    }
}
