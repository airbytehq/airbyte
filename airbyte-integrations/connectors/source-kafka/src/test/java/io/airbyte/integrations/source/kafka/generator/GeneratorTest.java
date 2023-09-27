/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.generator;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.kafka.KafkaMessage;
import io.airbyte.integrations.source.kafka.mediator.KafkaMediator;
import io.airbyte.integrations.source.kafka.state.State;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Queue;
import java.util.Set;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.StreamSupport;
import org.apache.kafka.common.TopicPartition;
import org.junit.jupiter.api.Test;

public class GeneratorTest {

  final int maxMessages = 1000;
  final int maxRetries = 10;

  @Test
  public void testOneBatchNoState() {
    final var mediator = new KafkaMediator() {

      final String topic = "topic-0";
      final Queue<KafkaMessage> messages = new LinkedList<>(
          List.of(
              new KafkaMessage(topic, 0, 0, new AirbyteRecordMessage().withStream(topic).withData(Jsons.deserialize("{ \"message\" : 1 }")))
          )
      );

      @Override
      public List<KafkaMessage> poll() {
        return Optional.ofNullable(this.messages.poll()).stream().toList();
      }

      @Override
      public Map<TopicPartition, Long> position(Set<TopicPartition> partitions) {
        return Map.of();
      }
    };
    final var generator = Generator.Builder.newInstance()
        .withMaxRecords(maxMessages)
        .withMaxRetries(maxRetries)
        .withMediator(mediator)
        .build();
    final var messages = StreamSupport.stream(
        Spliterators.spliteratorUnknownSize(generator.read(), Spliterator.ORDERED), false
    ).toList();
    final var expectedRecord = Jsons.deserialize("{ \"message\" : 1 }");

    assertAll(
        () -> assertEquals(1, messages.size()),
        () -> assertEquals(AirbyteMessage.Type.RECORD, messages.get(0).getType()),
        () -> assertEquals(expectedRecord, messages.get(0).getRecord().getData())
    );
  }

  @Test
  public void testOneBatchWithState() {
    final var mediator = new KafkaMediator() {

      final String topic = "topic-0";
      final Queue<List<KafkaMessage>> messages = new LinkedList<>(
          List.of(
              List.of(
                  new KafkaMessage(this.topic, 0, 0L,
                      new AirbyteRecordMessage().withStream(this.topic).withData(Jsons.deserialize("{ \"message\" : 2 }"))),
                  new KafkaMessage(this.topic, 1, 5L,
                      new AirbyteRecordMessage().withStream(this.topic).withData(Jsons.deserialize("{ \"message\" : 3 }")))
              )
          )
      );

      @Override
      public List<KafkaMessage> poll() {
        return Optional.ofNullable(this.messages.poll()).orElse(List.of());
      }

      @Override
      public Map<TopicPartition, Long> position(Set<TopicPartition> partitions) {
        return Map.ofEntries(
            Map.entry(new TopicPartition(this.topic, 0), 0L),
            Map.entry(new TopicPartition(this.topic, 1), 5L)
        );
      }
    };
    final var generator = Generator.Builder.newInstance()
        .withMaxRecords(maxMessages)
        .withMaxRetries(maxRetries)
        .withMediator(mediator)
        .build();
    final var messages = StreamSupport.stream(
        Spliterators.spliteratorUnknownSize(generator.read(), Spliterator.ORDERED), false
    ).toList();
    final var expectedRecord1 = Jsons.deserialize("{ \"message\" : 2 }");
    final var expectedRecord2 = Jsons.deserialize("{ \"message\" : 3 }");
    final var expectedStateTopic = "topic-0";
    final var expectedStateContent = Jsons.jsonNode(new State(Map.ofEntries(
        Map.entry(0, 0L),
        Map.entry(1, 5L)
    )));

    assertAll(
        () -> assertEquals(3, messages.size()),
        () -> assertEquals(AirbyteMessage.Type.RECORD, messages.get(0).getType()),
        () -> assertEquals(expectedRecord1, messages.get(0).getRecord().getData()),
        () -> assertEquals(AirbyteMessage.Type.RECORD, messages.get(1).getType()),
        () -> assertEquals(expectedRecord2, messages.get(1).getRecord().getData()),
        () -> assertEquals(AirbyteMessage.Type.STATE, messages.get(2).getType()),
        () -> assertEquals(AirbyteStateType.STREAM, messages.get(2).getState().getType()),
        () -> assertEquals(expectedStateTopic, messages.get(2).getState().getStream().getStreamDescriptor().getName()),
        () -> assertEquals(expectedStateContent, messages.get(2).getState().getStream().getStreamState())
    );
  }

  @Test
  public void testMultipleBatches() {
    final var mediator = new KafkaMediator() {

      final String topic0 = "topic-0";
      final String topic1 = "topic-2";

      final Queue<List<KafkaMessage>> messages = new LinkedList<>(
          List.of(
              List.of(
                  new KafkaMessage(this.topic0, 0, 0L,
                      new AirbyteRecordMessage().withStream(this.topic0).withData(Jsons.deserialize("{ \"message\" : 4 }")))
              ),
              List.of(
                  new KafkaMessage(this.topic1, 1, 5L,
                      new AirbyteRecordMessage().withStream(this.topic1).withData(Jsons.deserialize("{ \"message\" : 5 }")))
              )
          )
      );
      final Queue<Map<TopicPartition, Long>> partitions = new LinkedList<>(
          List.of(
              Map.of(new TopicPartition(this.topic0, 0), 0L),
              Map.of(new TopicPartition(this.topic1, 1), 5L)
          )
      );

      @Override
      public List<KafkaMessage> poll() {
        return Optional.ofNullable(this.messages.poll()).orElse(List.of());
      }

      @Override
      public Map<TopicPartition, Long> position(Set<TopicPartition> partitions) {
        return Optional.ofNullable(this.partitions.poll()).orElse(Map.of());
      }
    };
    final var generator = Generator.Builder.newInstance()
        .withMaxRecords(maxMessages)
        .withMaxRetries(maxRetries)
        .withMediator(mediator)
        .build();
    final var messages = StreamSupport.stream(
        Spliterators.spliteratorUnknownSize(generator.read(), Spliterator.ORDERED), false
    ).toList();
    final var expectedRecord1 = Jsons.deserialize("{ \"message\" : 4 }");
    final var expectedRecord2 = Jsons.deserialize("{ \"message\" : 5 }");
    final var expectedStateTopic1 = "topic-0";
    final var expectedStateContent1 = Jsons.jsonNode(new State(Map.ofEntries(
        Map.entry(0, 0L)
    )));
    final var expectedStateTopic2 = "topic-2";
    final var expectedStateContent2 = Jsons.jsonNode(new State(Map.ofEntries(
        Map.entry(1, 5L)
    )));

    assertAll(
        () -> assertEquals(4, messages.size()),
        () -> assertEquals(AirbyteMessage.Type.RECORD, messages.get(0).getType()),
        () -> assertEquals(expectedRecord1, messages.get(0).getRecord().getData()),
        () -> assertEquals(AirbyteMessage.Type.STATE, messages.get(1).getType()),
        () -> assertEquals(AirbyteStateType.STREAM, messages.get(1).getState().getType()),
        () -> assertEquals(expectedStateTopic1, messages.get(1).getState().getStream().getStreamDescriptor().getName()),
        () -> assertEquals(expectedStateContent1, messages.get(1).getState().getStream().getStreamState()),
        () -> assertEquals(AirbyteMessage.Type.RECORD, messages.get(2).getType()),
        () -> assertEquals(expectedRecord2, messages.get(2).getRecord().getData()),
        () -> assertEquals(AirbyteMessage.Type.STATE, messages.get(3).getType()),
        () -> assertEquals(AirbyteStateType.STREAM, messages.get(3).getState().getType()),
        () -> assertEquals(expectedStateTopic2, messages.get(3).getState().getStream().getStreamDescriptor().getName()),
        () -> assertEquals(expectedStateContent2, messages.get(3).getState().getStream().getStreamState())
    );
  }

  @Test
  public void testRetriesNoData() {
    final var mediator = new KafkaMediator() {

      @Override
      public List<KafkaMessage> poll() {
        return List.of();
      }

      @Override
      public Map<TopicPartition, Long> position(Set<TopicPartition> partitions) {
        return Map.of();
      }
    };
    final var generator = Generator.Builder.newInstance()
        .withMaxRecords(maxMessages)
        .withMaxRetries(maxRetries)
        .withMediator(mediator)
        .build();
    final var messages = StreamSupport.stream(
        Spliterators.spliteratorUnknownSize(generator.read(), Spliterator.ORDERED), false
    ).toList();

    assertTrue(messages.isEmpty());
  }

  @Test
  public void testRetriesDataAfterSomeAttempts() {
    final var mediator = new KafkaMediator() {

      final String topic = "topic-0";
      final Queue<List<KafkaMessage>> messages = new LinkedList<>(
          List.of(
              List.of(),
              List.of(),
              List.of(),
              List.of(),
              List.of(
                  new KafkaMessage(this.topic, 0, 0L,
                      new AirbyteRecordMessage().withStream(this.topic).withData(Jsons.deserialize("{ \"message\" : 6 }")))
              )
          )
      );

      @Override
      public List<KafkaMessage> poll() {
        return Optional.ofNullable(this.messages.poll()).orElse(List.of());
      }

      @Override
      public Map<TopicPartition, Long> position(Set<TopicPartition> partitions) {
        return Map.ofEntries(
            Map.entry(new TopicPartition(this.topic, 0), 0L)
        );
      }
    };
    final var generator = Generator.Builder.newInstance()
        .withMaxRecords(maxMessages)
        .withMaxRetries(maxRetries)
        .withMediator(mediator)
        .build();
    final var messages = StreamSupport.stream(
        Spliterators.spliteratorUnknownSize(generator.read(), Spliterator.ORDERED), false
    ).toList();
    final var expectedRecord = Jsons.deserialize("{ \"message\" : 6 }");
    final var expectedStateTopic = "topic-0";
    final var expectedStateContent = Jsons.jsonNode(new State(Map.ofEntries(
        Map.entry(0, 0L)
    )));

    assertAll(
        () -> assertEquals(2, messages.size()),
        () -> assertEquals(AirbyteMessage.Type.RECORD, messages.get(0).getType()),
        () -> assertEquals(expectedRecord, messages.get(0).getRecord().getData()),
        () -> assertEquals(AirbyteMessage.Type.STATE, messages.get(1).getType()),
        () -> assertEquals(AirbyteStateType.STREAM, messages.get(1).getState().getType()),
        () -> assertEquals(expectedStateTopic, messages.get(1).getState().getStream().getStreamDescriptor().getName()),
        () -> assertEquals(expectedStateContent, messages.get(1).getState().getStream().getStreamState())
    );
  }
}
