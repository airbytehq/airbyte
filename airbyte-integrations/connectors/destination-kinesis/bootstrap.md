# Kinesis Destination

Amazon Kinesis makes it easy to collect, process, and analyze real-time, streaming data so you can get timely insights and react quickly to new information. Amazon Kinesis offers key capabilities to cost-effectively process streaming data at any scale, along with the flexibility to choose the tools that best suit the requirements of your application.
You can use Kinesis Data Streams for rapid and continuous data intake and aggregation. The type of data used can include IT infrastructure log data, application logs, social media, market data feeds, and web clickstream data. Because the response time for the data intake and processing is in real time, the processing is typically lightweight.
[Read more about Amazon Kinesis](https://aws.amazon.com/kinesis/)

This connector maps an incoming Airbyte namespace and stream to a different Kinesis stream created and configured  with the provided shard count. The connector
supports the `append` sync mode which enables records to be directly streamed to an existing Kinesis stream.

The implementation uses the [Kinesis](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/examples-kinesis.html) Aws v2 Java Sdk to access the Kinesis service.
[KinesisStream](./src/main/java/io/airbyte/integrations/destination/kinesis/KinesisStream.java) is the main entrypoint for communicating with Kinesis and providing the needed functionalities. Internally it uses a KinesisClient retreived from the
[KinesisClientPool](./src/main/java/io/airbyte/integrations/destination/kinesis/KinesisClientPool.java). Retrieved records from the Kinesis stream are mapped to
[KinesisRecord](./src/main/java/io/airbyte/integrations/destination/kinesis/KinesisRecord.java). Buffering of records is also supported which should increase performance and throughput by sending the records through a single HTTP request.

The [KinesisMessageConsumer](./src/main/java/io/airbyte/integrations/destination/kinesis/KinesisMessageConsumer.java)
class contains the logic for handling airbyte messages, creating the needed Kinesis streams and streaming the received data.

## Development

See the [KinesisStream](./src/main/java/io/airbyte/integrations/destination/kinesis/KinesisStream.java) class on how to use the Kinesis client for accessing the Kinesis service.

If you want to learn more, read the [Aws docs](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/examples-kinesis.html)