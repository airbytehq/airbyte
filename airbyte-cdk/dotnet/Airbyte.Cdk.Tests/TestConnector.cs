using System.IO;
using Airbyte.Cdk.Sources.Utils;
using FluentAssertions;
using Xunit;

namespace Airbyte.Cdk.Tests
{
    public class TestConnector
    {
        [Fact]
        public void TestReadConfig()
        {
            var testfile = "{\"bogus\": \"file\"}";
            string filepath = "TestReadConfig";
            if (File.Exists(filepath))
                File.Delete(filepath);
            File.WriteAllText(filepath, testfile);

            var result = Connector.ReadConfig(filepath);

            result.GetRawText().Should().Be(testfile, "output should match input");
        }

        [Fact]
        public void TestWriteConfig()
        {
            var testfile = "{\"bogus\": \"file\"}";
            string filepath = "TestWriteConfig";
            
            Connector.WriteConfig(testfile.AsJsonElement(), filepath);

            var result = File.ReadAllText(filepath);

            result.Should().Be(testfile, "output should match input");
        }
    }
}
