using CommandLine;

namespace Airbyte.Cdk
{
    public abstract class Options
    {
        [Option('f', "config", HelpText = "Config file location")]
        public string Config { get; set; }

        [Option('l', "catalog", HelpText = "Catalog file location")]
        public string Catalog { get; set; }

        public virtual string Command { get; set; }
    }
}
