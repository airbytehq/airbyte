using CommandLine;

namespace Airbyte.Cdk
{
    [Verb("write", HelpText = "Writes data to the destination")]
    public class WriteOptions : Options
    {
        [Option('c', "command", Required = true, HelpText = "Command to execute [spec, check]")]
        public override string Command { get; set; }
    }
}
