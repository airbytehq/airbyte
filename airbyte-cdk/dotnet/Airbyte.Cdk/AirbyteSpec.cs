using System.IO;

namespace Airbyte.Cdk
{
    public class AirbyteSpec
    {
        public string SpecString { get; }

        public AirbyteSpec(string specstring) => SpecString = specstring;

        public static AirbyteSpec FromFile(string filename) => new (File.ReadAllText(filename));
    }
}
