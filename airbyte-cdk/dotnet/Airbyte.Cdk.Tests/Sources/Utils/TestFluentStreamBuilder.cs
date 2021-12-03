using System.Linq;
using System.Text.Json;
using Airbyte.Cdk.Sources.Utils;
using FluentAssertions;
using Flurl.Http;
using Moq;
using Xunit;

namespace Airbyte.Cdk.Tests.Sources.Utils
{
    public class TestFluentStreamBuilder
    {
        private string input_json =
            "{\"firstName\":\"John\",\"lastName\":\"doe\",\"age\":26,\"address\":{\"streetAddress\":\"naist street\",\"city\":\"Nara\",\"postalCode\":\"630-0192\"},\"phoneNumbers\":[{\"type\":\"iPhone\",\"number\":\"0123-4567-8888\"},{\"type\":\"home\",\"number\":\"0123-4567-8910\"}]}";

        [Fact]
        public void Test_ParseResponseObject_Root()
        {
            FluentStreamBuilder client = new FluentStreamBuilder();
            var func = client.ParseResponseObject("$");
            Mock<IFlurlResponse> response = new Mock<IFlurlResponse>();
            response.Setup(x => x.GetStringAsync().Result).Returns(input_json);

            var result = func.Create("x").ParseResponse(response.Object, "".AsJsonElement());

            result.First().GetRawText().Length.Should().Be(input_json.Length);
        }

        [Fact]
        public void Test_ParseResponseObject_ChildObjects()
        {
            FluentStreamBuilder client = new FluentStreamBuilder();
            var func = client.ParseResponseObject("$.address");
            Mock<IFlurlResponse> response = new Mock<IFlurlResponse>();
            response.Setup(x => x.GetStringAsync().Result).Returns(input_json);

            var expectedsresult = "{\"streetAddress\":\"naist street\",\"city\":\"Nara\",\"postalCode\":\"630-0192\"}";

            var result = func.Create("x").ParseResponse(response.Object,  "".AsJsonElement());

            result.First().GetRawText().Should().Be(expectedsresult);
        }

        [Fact]
        public void Test_ParseResponseObject_ChildObjects_NotFound()
        {
            FluentStreamBuilder client = new FluentStreamBuilder();
            var func = client.ParseResponseObject("$.addresses");
            Mock<IFlurlResponse> response = new Mock<IFlurlResponse>();
            response.Setup(x => x.GetStringAsync().Result).Returns(input_json);

            var result = func.Create("x").ParseResponse(response.Object, "".AsJsonElement());

            result.Should().BeEmpty();
        }

        [Fact]
        public void Test_ParseResponseObject_SingleChildObjects()
        {
            FluentStreamBuilder client = new FluentStreamBuilder();
            var func = client.ParseResponseArray("$.phoneNumbers[0]");
            Mock<IFlurlResponse> response = new Mock<IFlurlResponse>();
            response.Setup(x => x.GetStringAsync().Result).Returns(input_json);

            var result = func.Create("x").ParseResponse(response.Object, "".AsJsonElement());

            result.Should().BeEmpty();
        }

        [Fact]
        public void Test_ParseResponseObject_Array()
        {
            FluentStreamBuilder client = new FluentStreamBuilder();
            var func = client.ParseResponseObject("$.phoneNumbers");
            Mock<IFlurlResponse> response = new Mock<IFlurlResponse>();
            response.Setup(x => x.GetStringAsync().Result).Returns(input_json);

            var result = func.Create("x").ParseResponse(response.Object, "".AsJsonElement());

            var items = result.First().EnumerateArray();
            items.Count().Should().Be(2);
        }

        [Fact]
        public void Test_ParseResponseArray()
        {
            FluentStreamBuilder client = new FluentStreamBuilder();
            var func = client.ParseResponseArray("$.phoneNumbers");
            Mock<IFlurlResponse> response = new Mock<IFlurlResponse>();
            response.Setup(x => x.GetStringAsync().Result).Returns(input_json);
            
            var result = func.Create("x").ParseResponse(response.Object, "".AsJsonElement());

            var jsonElements = result as JsonElement[] ?? result.ToArray();
            jsonElements.Count().Should().Be(2);
            jsonElements.First().GetProperty("type").GetString().Should().Be("iPhone");
            jsonElements.ToArray()[1].GetProperty("type").GetString().Should().Be("home");
        }


        [Fact]
        public void Test_ParseResponseArray_Root()
        {
            var expectedsresult = "[{\"type\":\"iPhone\",\"number\":\"0123-4567-8888\"},{\"type\":\"home\",\"number\":\"0123-4567-8910\"}]";
            FluentStreamBuilder client = new FluentStreamBuilder();
            var func = client.ParseResponseArray("$");
            Mock<IFlurlResponse> response = new Mock<IFlurlResponse>();
            response.Setup(x => x.GetStringAsync().Result).Returns(expectedsresult);
            
            var result = func.Create("x").ParseResponse(response.Object, "".AsJsonElement());

            var jsonElements = result as JsonElement[] ?? result.ToArray();
            jsonElements.Count().Should().Be(2);
            jsonElements.First().GetProperty("type").GetString().Should().Be("iPhone");
            jsonElements.ToArray()[1].GetProperty("type").GetString().Should().Be("home");
        }
    }
}
