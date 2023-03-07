/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.Closeable;
import java.util.Collection;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.errors.TopicExistsException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedpandaOperations implements Closeable {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedpandaOperations.class);

  private final Admin adminClient;

  private final KafkaProducer<String, JsonNode> kafkaProducer;

  public RedpandaOperations(RedpandaConfig redpandaConfig) {
    this.adminClient = redpandaConfig.createAdminClient();
    this.kafkaProducer = redpandaConfig.createKafkaProducer();
  }

  public void createTopic(Collection<TopicInfo> topics) {
    var newTopics = topics.stream()
        .map(tf -> new NewTopic(tf.name(), tf.numPartitions(), tf.replicationFactor()))
        .collect(Collectors.toSet());

    var createTopicsResult = adminClient.createTopics(newTopics);

    // we need to wait for results since data replication is directly dependent on topic creation

    createTopicsResult.values().values().forEach(f -> {
      try {
        syncWrapper(() -> f);
      } catch (ExecutionException e) {
        // errors related to already existing topics should be ignored
        if (!(e.getCause() instanceof TopicExistsException)) {
          throw new RuntimeException(e);
        }
      }
    });
  }

  public void deleteTopic(Collection<String> topics) {

    var deleteTopicsResult = adminClient.deleteTopics(topics);

    try {
      syncWrapper(deleteTopicsResult::all);
    } catch (ExecutionException e) {
      throw new RuntimeException(e);
    }
  }

  public Set<String> listTopics() {

    var listTopics = adminClient.listTopics();

    try {
      return syncWrapper(listTopics::names);
    } catch (ExecutionException e) {
      throw new RuntimeException(e);
    }

  }

  public void putRecord(String topic, String key, JsonNode data, Consumer<Exception> consumer) {
    var producerRecord = new ProducerRecord<>(topic, key, data);

    kafkaProducer.send(producerRecord, ((metadata, exception) -> {
      if (exception != null) {
        consumer.accept(exception);
      }
    }));

  }

  // used when testing write permissions on check
  public void putRecordBlocking(String topic, String key, JsonNode data) {

    var producerRecord = new ProducerRecord<>(topic, key, data);

    try {
      syncWrapper(kafkaProducer::send, producerRecord);
    } catch (ExecutionException e) {
      throw new RuntimeException(e);
    }
  }

  public void flush() {
    kafkaProducer.flush();
  }

  private <T> T syncWrapper(Supplier<Future<T>> asyncFunction) throws ExecutionException {
    try {
      return asyncFunction.get().get();
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new RuntimeException(e);
    }
  }

  private <T> T syncWrapper(Function<ProducerRecord<String, JsonNode>, Future<T>> asyncFunction,
                            ProducerRecord<String, JsonNode> producerRecord)
      throws ExecutionException {
    return syncWrapper(() -> asyncFunction.apply(producerRecord));
  }

  public record TopicInfo(

                          String name,

                          Optional<Integer> numPartitions,

                          Optional<Short> replicationFactor

  ) {

  }

  @Override
  public void close() {
    kafkaProducer.flush();
    kafkaProducer.close();
    adminClient.close();
  }

}
