/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.commons.json.Jsons;
import java.time.Instant;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import software.amazon.awssdk.services.kinesis.model.ResourceNotFoundException;

class KinesisStreamTest {

  private static KinesisContainerInitializr.KinesisContainer kinesisContainer;

  private KinesisStream kinesisStream;

  @BeforeAll
  static void setup() {
    kinesisContainer = KinesisContainerInitializr.initContainer();
  }

  @BeforeEach
  void init() {
    var jsonConfig = KinesisDataFactory.jsonConfig(
        kinesisContainer.getEndpointOverride().toString(),
        kinesisContainer.getRegion(),
        kinesisContainer.getAccessKey(),
        kinesisContainer.getSecretKey());
    this.kinesisStream = new KinesisStream(new KinesisConfig(jsonConfig));
  }

  @AfterEach
  void cleanup() {
    kinesisStream.deleteAllStreams();
  }

  @Test
  void testCreateStream() {
    String streamName = "test_create_stream";
    // given
    kinesisStream.createStream(streamName);
    kinesisStream.flush(e -> {});
    // when
    var records = kinesisStream.getRecords(streamName);

    // then
    assertThat(records)
        .isNotNull()
        .hasSize(0);

  }

  @Test
  void testDeleteStream() {
    String streamName = "test_delete_stream";
    // given
    kinesisStream.createStream(streamName);

    // when
    kinesisStream.deleteStream(streamName);

    // then
    assertThrows(ResourceNotFoundException.class, () -> kinesisStream.getRecords(streamName));
  }

  @Test
  void testDeleteAllStreams() {
    var streamName1 = "test_delete_all_stream1";
    var streamName2 = "test_delete_all_stream2";
    // given
    kinesisStream.createStream(streamName1);
    kinesisStream.createStream(streamName2);

    // when
    kinesisStream.deleteAllStreams();

    // then
    assertThrows(ResourceNotFoundException.class, () -> kinesisStream.getRecords(streamName1));
    assertThrows(ResourceNotFoundException.class, () -> kinesisStream.getRecords(streamName2));

  }

  @Test
  void testPutRecordAndFlush() {
    // given
    String streamName = "test_put_record_stream";
    kinesisStream.createStream(streamName);

    var partitionKey1 = KinesisUtils.buildPartitionKey();
    kinesisStream.putRecord(streamName, partitionKey1, createData(partitionKey1, "{\"property\":\"data1\"}"),
        e -> {});

    var partitionKey2 = KinesisUtils.buildPartitionKey();
    kinesisStream.putRecord(streamName, partitionKey2, createData(partitionKey2, "{\"property\":\"data2\"}"),
        e -> {});

    kinesisStream.flush(e -> {});

    // when
    var records = kinesisStream.getRecords(streamName);

    // then
    assertThat(records)
        .isNotNull()
        .hasSize(2)
        .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"));
  }

  private String createData(String partitionKey, String data) {
    var kinesisRecord = Jsons.jsonNode(Map.of(
        KinesisRecord.COLUMN_NAME_AB_ID, partitionKey,
        KinesisRecord.COLUMN_NAME_DATA, data,
        KinesisRecord.COLUMN_NAME_EMITTED_AT, Instant.now()));
    return Jsons.serialize(kinesisRecord);
  }

}
