using System;
using System.Text.Json;
using Airbyte.Cdk.Models;
using Airbyte.Cdk.Sources;
using Airbyte.Cdk.Sources.Streams;
using Airbyte.Cdk.Sources.Utils;
using FluentAssertions;
using Moq;
using Xunit;

namespace Airbyte.Cdk.Tests.Sources
{
    public class TestAbstractSource
    {
        public Mock<AirbyteLogger> Logger { get; } = new();

        public Mock<MockSource> Mock { get; } = new();

        [Fact]
        public void TestSuccesfullConnection()
        {
            Exception noexc = null;
            Mock.Setup(
                    (source => source.CheckConnection(It.IsAny<AirbyteLogger>(), It.IsAny<JsonElement>(), out noexc)))
                .Returns(true);
            Mock.CallBase = true;

            var result = Mock.Object.Check(Logger.Object, "".AsJsonElement());

            result.Should().NotBeNull();
            result.Status.Should().Be(Status.SUCCEEDED);
        }

        [Fact]
        public void TestFailedConnection()
        {
            string exceptionmessage = "Cannot execute due to incorrect code!";
            Exception exception = new Exception(exceptionmessage);
            Mock.Setup(
                    (source => source.CheckConnection(It.IsAny<AirbyteLogger>(), It.IsAny<JsonElement>(), out exception)))
                .Returns(false);
            Mock.CallBase = true;

            var result = Mock.Object.Check(Logger.Object,"".AsJsonElement());

            result.Should().NotBeNull();
            result.Status.Should().Be(Status.FAILED);
            result.Message.Should().NotBeNullOrWhiteSpace();
            result.Message.Should().Be(exceptionmessage);
        }

        [Fact]
        public void TestDiscover()
        {
            var airbytestream_1 = new AirbyteStream
            {
                Name = "1",
                JsonSchema = "{}".AsJsonElement(),
                SupportedSyncModes = new[] { SyncMode.full_refresh, SyncMode.incremental },
                DefaultCursorField = new[] { "cursor" },
                SourceDefinedCursor = true
            };

            var airbytestream_2 = new AirbyteStream
            {
                Name = "2",
                JsonSchema = "{}".AsJsonElement(),
                SupportedSyncModes = new[] { SyncMode.full_refresh }
            };

            var stream1 = new Mock<Stream>();
            stream1.Setup(stream => stream.AsAirbyteStream()).Returns(airbytestream_1);

            var stream2 = new Mock<Stream>();
            stream2.Setup(stream => stream.AsAirbyteStream()).Returns(airbytestream_2);

            var expectedresult = new AirbyteCatalog
            {
                Streams = new[] { airbytestream_1, airbytestream_2 }
            };

            var returns = new[] { stream1.Object, stream2.Object };
            Mock.Setup(source => source.Streams(It.IsAny<JsonElement>())).Returns(returns);
            Mock.CallBase = true;

            var result = Mock.Object.Discover(Logger.Object, "".AsJsonElement());

            result.Should().NotBeNull();
            result.Streams.Length.Should().Be(expectedresult.Streams.Length);
            result.Streams[0].Should().BeSameAs(expectedresult.Streams[0]);
            result.Streams[1].Should().BeSameAs(expectedresult.Streams[1]);
        }

        [Fact(Skip = "Not Implemented")]
        public void TestReadNonexistentStreamRaisesException()
        {

        }

        [Fact(Skip = "Not Implemented")]
        public void TestValidFullRefreshReadNoSlices()
        {
            
        }

        [Fact(Skip = "Not Implemented")]
        public void TestValidFullRefreshReadWithSlices()
        {
            
        }

        [Fact(Skip = "Not Implemented")]
        public void TestValidIncrementalReadWithCheckpointInterval()
        {
            
        }

        [Fact(Skip = "Not Implemented")]
        public void TestValidIncrementalReadWithNoInterval()
        {
            
        }

        [Fact(Skip = "Not Implemented")]
        public void TestValidIncrementalReadWithSlices()
        {
            
        }

        [Fact(Skip = "Not Implemented")]
        public void TestValidIncrementalReadWithSlicesAndInterval()
        {
            
        }
    }

    public class MockSource : AbstractSource
    {
        public override bool CheckConnection(AirbyteLogger logger, JsonElement config, out Exception exc)
        {
            throw new NotImplementedException();
        }

        public override Stream[] Streams(JsonElement config)
        {
            throw new NotImplementedException();
        }
    }
}
