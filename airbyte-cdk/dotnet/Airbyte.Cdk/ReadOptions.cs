using CommandLine;

namespace Airbyte.Cdk
{
    [Verb("read", HelpText = "Reads data from a source")]
    public class ReadOptions : Options
    {
        [Option('c', "command", Required = true, HelpText = "Command to execute [spec, check, discover]")]
        public override string Command { get; set; }

        [Option('s', "state", Required = false, HelpText = "path to the json-encoded state file")]
        public string State { get; set; }
    }
}
