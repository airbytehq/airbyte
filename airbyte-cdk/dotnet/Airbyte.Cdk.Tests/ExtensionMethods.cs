using System.Collections.Generic;
using System.Text.Json;
using Airbyte.Cdk.Models;
using Airbyte.Cdk.Sources.Utils;
using FluentAssertions;
using Xunit;

namespace Airbyte.Cdk.Tests
{
    public class ExtensionMethods
    {
        [Fact]
        public void AsJsonDocumentFromString()
        {
            var jsonobject = "{\"bogus\": \"json\"}";

            var result = jsonobject.AsJsonElement();

            result.GetRawText().Should().Be(jsonobject, "the raw text should stay the same");
            result.ValueKind.Should().Be(JsonValueKind.Object, "we provided a json object");
        }

        [Fact]
        public void AsJsonDocumentFromObject()
        {
            var jsonobject = new AirbyteRecordMessage();

            var result = jsonobject.AsJsonElement();

            result.ValueKind.Should().Be(JsonValueKind.Object, "we provided a json object");
        }

        [Fact]
        public void JsonDocumentToType()
        {
            var input = new Dictionary<string, int>
            {
                {"hello", 1},
                {"world", 2},
                {"!", 3}
            };
            var jsonDocument = input.AsJsonElement();

            var result = jsonDocument.ToType<Dictionary<string, int>>();

            result.Should().Equal(input, "the output should match the input");
        }
    }
}
