/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.generator;

import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.kafka.KafkaMessage;
import io.airbyte.integrations.source.kafka.mediator.KafkaMediator;
import io.airbyte.integrations.source.kafka.state.StateHelper;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.Set;
import org.apache.kafka.common.TopicPartition;

final public class Generator {

  private final KafkaMediator mediator;
  private final int maxRecords;
  private final int maxRetries;

  public Generator(Builder builder) {
    this.maxRecords = builder.maxRecords;
    this.maxRetries = builder.maxRetries;
    this.mediator = builder.mediator;
  }

  public static class Builder {

    private KafkaMediator mediator;
    private int maxRecords = 100000;
    private int maxRetries = 10;

    public static Builder newInstance() {
      return new Builder();
    }

    private Builder() {
    }

    public Builder withMaxRecords(int maxRecords) {
      this.maxRecords = maxRecords;
      return this;
    }

    public Builder withMaxRetries(int maxRetries) {
      this.maxRetries = maxRetries;
      return this;
    }

    public Builder withMediator(KafkaMediator mediator) {
      this.mediator = mediator;
      return this;
    }

    public Generator build() {
      return new Generator(this);
    }

  }

  public AutoCloseableIterator<AirbyteMessage> read() {

    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      private int totalRead = 0;
      private final Queue<AirbyteMessage> pendingMessages = new LinkedList<>();

      @Override
      protected AirbyteMessage computeNext() {
        if (this.pendingMessages.isEmpty()) {
          if (this.totalRead < Generator.this.maxRecords) {
            List<KafkaMessage> batch = pullBatchFromKafka();
            if (!batch.isEmpty()) {
              this.totalRead += batch.size();
              this.pendingMessages.addAll(convertToAirbyteMessagesWithState(batch));
            }
          } else {
            return endOfData();
          }
        }

        // If no more pending kafka records, close iterator
        if (this.pendingMessages.isEmpty()) {
          return endOfData();
        } else {
          return pendingMessages.poll();
        }
      }

      private List<AirbyteMessage> convertToAirbyteMessagesWithState(List<KafkaMessage> batch) {
        final Set<TopicPartition> partitions = new HashSet<>();
        final List<AirbyteMessage> messages = new ArrayList<>();

        for (KafkaMessage entry : batch) {
          final var topic = entry.topic();
          final var partition = entry.partition();
          final var message = entry.message();
          partitions.add(new TopicPartition(topic, partition));
          messages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(message));
        }

        final var offsets = Generator.this.mediator.position(partitions);

        for (AirbyteStateMessage entry : StateHelper.toAirbyteState(offsets)) {
          messages.add(new AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(entry));
        }

        return messages;
      }

      private List<KafkaMessage> pullBatchFromKafka() {
        List<KafkaMessage> batch;
        var nrOfRetries = 0;
        do {
          batch = Generator.this.mediator.poll();
        } while (batch.isEmpty() && ++nrOfRetries < Generator.this.maxRetries);
        return batch;
      }
    });
  }
}
