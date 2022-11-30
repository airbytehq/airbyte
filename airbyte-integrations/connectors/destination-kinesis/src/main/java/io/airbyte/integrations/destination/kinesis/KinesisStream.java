/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import io.airbyte.commons.json.Jsons;
import java.io.Closeable;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.core.BytesWrapper;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kinesis.KinesisClient;
import software.amazon.awssdk.services.kinesis.model.DescribeStreamResponse;
import software.amazon.awssdk.services.kinesis.model.PutRecordsRequestEntry;
import software.amazon.awssdk.services.kinesis.model.Record;
import software.amazon.awssdk.services.kinesis.model.ResourceInUseException;
import software.amazon.awssdk.services.kinesis.model.ResourceNotFoundException;
import software.amazon.awssdk.services.kinesis.model.Shard;
import software.amazon.awssdk.services.kinesis.model.ShardIteratorType;
import software.amazon.awssdk.services.kinesis.model.StreamStatus;

/**
 * KinesisStream class for performing various operations on a Kinesis stream.
 */
public class KinesisStream implements Closeable {

  private static final Logger LOGGER = LoggerFactory.getLogger(KinesisStream.class);

  private final KinesisClient kinesisClient;

  private final KinesisConfig kinesisConfig;

  private final int bufferSize;

  // k:v tuples of <streamName:<partitionKey,data>>
  private final List<Tuple<String, Tuple<String, String>>> buffer;

  public KinesisStream(KinesisConfig kinesisConfig) {
    this.kinesisConfig = kinesisConfig;
    this.kinesisClient = KinesisClientPool.initClient(kinesisConfig);
    this.bufferSize = kinesisConfig.getBufferSize();
    this.buffer = new ArrayList<>(bufferSize);
  }

  /**
   * Creates a stream specified via its name and with the provided shard count. The method will block
   * and retry every 2s until it verifies that the stream is active and can be written to. If the
   * stream is already created it will only wait until it is active.
   *
   * @param streamName name of the stream to be created.
   */
  public void createStream(String streamName) {
    try {
      kinesisClient.createStream(b -> b.streamName(streamName).shardCount(kinesisConfig.getShardCount()));
    } catch (ResourceInUseException e) {
      LOGGER.info("Stream with name {} has already been created", streamName);
    }
    // block/wait until stream is active
    for (;;) {
      DescribeStreamResponse describeStream = kinesisClient.describeStream(b -> b.streamName(streamName));
      if (describeStream.streamDescription().streamStatus() == StreamStatus.ACTIVE) {
        return;
      }
      try {
        Thread.sleep(2000);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        throw KinesisUtils.buildKinesisException("Thread interrupted while waiting for stream to be active", e);
      }
    }
  }

  /**
   * Delete the stream specified via its name. The method will block and retry every 2s until it
   * verifies that the stream is deleted by receiving the appropriate exception.
   *
   * @param streamName name of the stream to be deleted.
   */
  public void deleteStream(String streamName) {
    kinesisClient.deleteStream(b -> b.streamName(streamName));
    // block/wait until stream is deleted
    for (;;) {
      try {
        kinesisClient.describeStream(b -> b.streamName(streamName));
        Thread.sleep(2000);
      } catch (ResourceNotFoundException e) {
        return;
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        throw KinesisUtils.buildKinesisException("Thread interrupted while waiting for stream to be deleted", e);
      }
    }
  }

  /**
   * Deletes all streams in the Kinesis service, waiting/blocking until all of them are deleted.
   */
  public void deleteAllStreams() {
    kinesisClient.listStreams().streamNames().forEach(this::deleteStream);
  }

  /**
   * Sends a record to the Kinesis stream specified via its name. To improve performance the records
   * are buffered until the buffer limit is reached after which they are flushed to its destination
   * stream.
   *
   * @param streamName name of the stream where the record should be sent
   * @param partitionKey to determine the destination shard
   * @param data actual data to be streamed
   * @param exceptionConsumer for handling errors related to flushing data per stream
   */
  public void putRecord(String streamName, String partitionKey, String data, Consumer<Exception> exceptionConsumer) {
    buffer.add(Tuple.of(streamName, Tuple.of(partitionKey, data)));
    if (buffer.size() == bufferSize) {
      flush(exceptionConsumer);
    }
  }

  /**
   * Iterates over all the shards for a given streams and retrieves the records which are combined and
   * deserialized to a {@link io.airbyte.integrations.destination.kinesis.KinesisRecord} objects.
   *
   * @param streamName from where to retrieve the records.
   * @return List of KinesisRecord objects retrieved from the stream.
   */
  public List<KinesisRecord> getRecords(String streamName) {
    DescribeStreamResponse describeStream;
    List<Shard> shards = new ArrayList<>();
    do {

      describeStream = kinesisClient.describeStream(b -> b.streamName(streamName));

      shards.addAll(describeStream.streamDescription().shards());

    } while (describeStream.streamDescription().hasMoreShards());

    // iterate over stream shards and retrieve records
    return shards.stream()
        .map(Shard::shardId)
        .map(sh -> kinesisClient.getShardIterator(b -> b.streamName(streamName)
            .shardIteratorType(ShardIteratorType.TRIM_HORIZON)
            .shardId(sh))
            .shardIterator())
        .flatMap(it -> kinesisClient.getRecords(b -> b.shardIterator(it)).records().stream())
        .map(Record::data)
        .map(BytesWrapper::asUtf8String)
        .map(str -> Jsons.deserialize(str, KinesisRecord.class))
        .collect(Collectors.toList());
  }

  /**
   * Flush all records previously buffered to increase throughput and performance. Records are grouped
   * by stream name and are sent for each stream separately.
   *
   * @param exceptionConsumer for handling errors related to flushing data per stream, rethrowing an
   *        exception in the consumer will stop the sync and clear the cache
   */
  public void flush(Consumer<Exception> exceptionConsumer) {
    try {
      buffer.stream()
          .collect(Collectors.groupingBy(Tuple::value1, Collectors.mapping(Tuple::value2, Collectors.toList())))
          .forEach((k, v) -> {
            var records = v.stream().map(entry -> PutRecordsRequestEntry.builder()
                // partition key used to determine stream shard.
                .partitionKey(entry.value1())
                .data(SdkBytes.fromUtf8String(entry.value2()))
                .build())
                .collect(Collectors.toList());
            try {
              kinesisClient.putRecords(b -> b.streamName(k).records(records));
            } catch (Exception e) {
              exceptionConsumer.accept(e);
            }
          });
    } finally {
      buffer.clear();
    }
  }

  /**
   * Return the kinesis client to the pool to be closed if no longer used.
   */
  @Override
  public void close() {
    KinesisClientPool.closeClient(kinesisConfig);
  }

}
