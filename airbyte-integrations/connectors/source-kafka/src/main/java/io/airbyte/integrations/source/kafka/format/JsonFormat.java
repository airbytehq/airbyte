//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package io.airbyte.integrations.source.kafka.format;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.Lists;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import javax.annotation.CheckForNull;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.connect.json.JsonDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JsonFormat extends AbstractFormat {
  private static final Logger LOGGER = LoggerFactory.getLogger(JsonFormat.class);
  private KafkaConsumer<String, JsonNode> consumer;

  public JsonFormat(JsonNode jsonConfig) {
    super(jsonConfig);
  }

  protected KafkaConsumer<String, JsonNode> getConsumer() {
    if (this.consumer != null) {
      return this.consumer;
    } else {
      Map<String, Object> filteredProps = this.getKafkaConfig();
      this.consumer = new KafkaConsumer(filteredProps);
      JsonNode subscription = this.config.get("subscription");
      LOGGER.info("Kafka subscribe method: {}", subscription.toString());
      String topicPartitions;
      switch (subscription.get("subscription_type").asText()) {
        case "subscribe":
          topicPartitions = subscription.get("topic_pattern").asText();
          this.consumer.subscribe(Pattern.compile(topicPartitions));
          this.topicsToSubscribe = (Set)this.consumer.listTopics().keySet().stream().filter((topic) -> {
            return topic.matches(topicPartitions);
          }).collect(Collectors.toSet());
          LOGGER.info("Topic list: {}", this.topicsToSubscribe);
          break;
        case "assign":
          this.topicsToSubscribe = new HashSet();
          topicPartitions = subscription.get("topic_partitions").asText();
          String[] topicPartitionsStr = topicPartitions.replaceAll("\\s+", "").split(",");
          List<TopicPartition> topicPartitionList = (List)Arrays.stream(topicPartitionsStr).map((topicPartition) -> {
            String[] pair = topicPartition.split(":");
            this.topicsToSubscribe.add(pair[0]);
            return new TopicPartition(pair[0], Integer.parseInt(pair[1]));
          }).collect(Collectors.toList());
          LOGGER.info("Topic-partition list: {}", topicPartitionList);
          this.consumer.assign(topicPartitionList);
      }
      return this.consumer;
    }
  }

  protected Map<String, Object> getKafkaConfig() {
    Map<String, Object> props = super.getKafkaConfig();
    props.put("key.deserializer", StringDeserializer.class.getName());
    props.put("value.deserializer", JsonDeserializer.class.getName());
    return props;
  }

  public Set<String> getTopicsToSubscribe() {
    if (this.topicsToSubscribe == null) {
      this.getConsumer();
    }

    return this.topicsToSubscribe;
  }

  public List<AirbyteStream> getStreams() {
    Set<String> topicsToSubscribe = this.getTopicsToSubscribe();
    List<AirbyteStream> streams = (List)topicsToSubscribe.stream().map((topic) -> {
      return CatalogHelpers.createAirbyteStream(topic, new Field[]{Field.of("value", JsonSchemaType.STRING)}).withSupportedSyncModes(Lists.newArrayList(new SyncMode[]{SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL}));
    }).collect(Collectors.toList());
    return streams;
  }

  public AutoCloseableIterator<AirbyteMessage> read(JsonNode state, List<String> topics) {
    KafkaConsumer<String, JsonNode> consumer = this.getConsumer();
    List<ConsumerRecord<String, JsonNode>> recordsList = new ArrayList();
    int retry = this.config.has("repeated_calls") ? this.config.get("repeated_calls").intValue() : 0;
    int polling_time = this.config.has("polling_time") ? this.config.get("polling_time").intValue() : 100;
    int max_records = this.config.has("max_records_process") ? this.config.get("max_records_process").intValue() : 100000;
    AtomicInteger record_count = new AtomicInteger();
    Map<String, Integer> poll_lookup = new HashMap();
    this.getTopicsToSubscribe().forEach((topic) -> {
      poll_lookup.put(topic, 0);
    });

    while(true) {
      ConsumerRecords<String, JsonNode> consumerRecords = consumer.poll(Duration.of((long)polling_time, ChronoUnit.MILLIS));
      consumerRecords.forEach((record) -> {
        record_count.getAndIncrement();
        recordsList.add(record);
      });
      consumer.commitAsync();
      if (consumerRecords.count() == 0) {
        consumer.assignment().stream().map((record) -> {
          return record.topic();
        }).distinct().forEach((topic) -> {
          poll_lookup.put(topic, (Integer)poll_lookup.get(topic) + 1);
        });
        boolean is_complete = poll_lookup.entrySet().stream().allMatch((e) -> {
          return (Integer)e.getValue() > retry;
        });
        if (is_complete) {
          LOGGER.info("There is no new data in the queue!!");
          break;
        }
      } else if (record_count.get() > max_records) {
        LOGGER.info("Max record count is reached !!");
        break;
      }
    }

    consumer.close();
    final Iterator<ConsumerRecord<String, JsonNode>> iterator = recordsList.iterator();
    return AutoCloseableIterators.fromIterator(new AbstractIterator<AirbyteMessage>() {
      protected AirbyteMessage computeNext() {
        if (iterator.hasNext()) {
          ConsumerRecord<String, JsonNode> record = (ConsumerRecord)iterator.next();
          return (new AirbyteMessage()).withType(Type.RECORD).withRecord((new AirbyteRecordMessage()).withStream(record.topic()).withEmittedAt(Instant.now().toEpochMilli()).withData((JsonNode)record.value()));
        } else {
          return (AirbyteMessage)this.endOfData();
        }
      }
    });
  }

  public boolean isAccessible() {
    try {
      String testTopic = this.config.has("test_topic") ? this.config.get("test_topic").asText() : "";
      if (!testTopic.isBlank()) {
        KafkaConsumer<String, JsonNode> consumer = this.getConsumer();
        consumer.subscribe(Pattern.compile(testTopic));
        consumer.listTopics();
        consumer.close();
        LOGGER.info("Successfully connected to Kafka brokers for topic '{}'.", this.config.get("test_topic").asText());
      }

      return true;
    } catch (Exception var3) {
      LOGGER.error("Exception attempting to connect to the Kafka brokers: ", var3);
      return false;
    }
  }

  @CheckForNull
  protected AirbyteMessage computeNext() {
    return null;
  }
}
