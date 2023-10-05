/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.kafka.AssignOffset;
import io.airbyte.integrations.source.kafka.KafkaStrategy;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.*;
import io.confluent.kafka.serializers.KafkaAvroDeserializer;

import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.apache.avro.generic.GenericRecord;
import org.apache.commons.lang3.StringUtils;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.CheckForNull;

public class AvroFormat extends AbstractFormat {
  private static final Logger LOGGER = LoggerFactory.getLogger(AvroFormat.class);
  private KafkaConsumer<String, GenericRecord> consumer;
  private List<ConsumerRecord<String, GenericRecord>> recordsList = new ArrayList();
  private Map<String, Map<Integer, Long>> stateData = new HashMap();

  private int record_index = 0;
  private boolean sendstatus = true;
  private String topicPattern;

  private int current_records=0;

  private final int max_records;

  public AvroFormat(JsonNode jsonConfig) {
    super(jsonConfig);
    max_records = config.has("max_records_process") ? config.get("max_records_process").intValue() : 100000;

  }

  protected Map<String, Object> getKafkaConfig() {
    Map<String, Object> props = super.getKafkaConfig();
    JsonNode avro_config = this.config.get("MessageFormat");
    props.put("key.deserializer", StringDeserializer.class.getName());
    props.put("value.deserializer", KafkaAvroDeserializer.class.getName());
    props.put("basic.auth.credentials.source", "USER_INFO");
    props.put("basic.auth.user.info", String.format("%s:%s", avro_config.get("schema_registry_username").asText(), avro_config.get("schema_registry_password").asText()));
    props.put("schema.registry.url", avro_config.get("schema_registry_url").asText());
    props.put("value.subject.name.strategy", KafkaStrategy.getStrategyName(avro_config.get("deserialization_strategy").asText()));
    return props;
  }

  protected KafkaConsumer<String, GenericRecord> getConsumer() {
    if (this.consumer != null) {
      return this.consumer;
    } else {
      Map<String, Object> filteredProps = this.getKafkaConfig();
      this.consumer = new KafkaConsumer(filteredProps);
      JsonNode subscription = this.config.get("subscription");
      LOGGER.info("Kafka subscribe method: {}", subscription.toString());
      String topicPattern;
      switch (subscription.get("subscription_type").asText()) {
        case "subscribe":
          topicPattern = subscription.get("topic_pattern").asText();
          if (iskafkaCheckpoint()) {
            this.consumer.subscribe(Pattern.compile(topicPattern));
          } else {
            this.consumer.subscribe(Pattern.compile(topicPattern), new AssignOffset(this.consumer, this.stateData));
          }
          this.topicsToSubscribe = (Set)this.consumer.listTopics().keySet().stream().filter((topic) -> {
            return topic.matches(topicPattern);
          }).collect(Collectors.toSet());
          LOGGER.info("Topic list: {}", this.topicsToSubscribe);
          break;
        case "assign":
          this.topicsToSubscribe = new HashSet();
          topicPattern = subscription.get("topic_partitions").asText();
          String[] topicPartitionsStr = topicPattern.replaceAll("\\s+", "").split(",");
          List<TopicPartition> topicPartitionList = (List)Arrays.stream(topicPartitionsStr).map((topicPartition) -> {
            String[] pair = topicPartition.split(":");
            this.topicsToSubscribe.add(pair[0]);
            return new TopicPartition(pair[0], Integer.parseInt(pair[1]));
          }).collect(Collectors.toList());
          LOGGER.info("Topic-partition list: {}", topicPartitionList);
          this.consumer.assign(topicPartitionList);
          if (iskafkaCheckpoint()) {
            topicPartitionList.stream().forEach(topicPartition -> {
              Map<Integer, Long> partitionoffsets = (Map) this.stateData.get(topicPartition.topic());
              if (partitionoffsets != null) {
                long lastoffset = (Long) partitionoffsets.get(topicPartition.partition());
                ++lastoffset;
                this.consumer.seek(topicPartition, lastoffset);
              }
            });
          }
      }
      return this.consumer;
    }
  }

  protected KafkaConsumer<String, GenericRecord> getConsumer(String topicPattern) {
    if (this.consumer != null) {
      return this.consumer;
    } else {
      Map<String, Object> filteredProps = this.getKafkaConfig();
      this.consumer = new KafkaConsumer(filteredProps);
      if (iskafkaCheckpoint()) {
        this.consumer.subscribe(Pattern.compile(topicPattern));
      } else {
        this.consumer.subscribe(Pattern.compile(topicPattern), new AssignOffset(this.consumer, this.stateData));
      }
      this.topicsToSubscribe = (Set)this.consumer.listTopics().keySet().stream().filter((topic) -> {
        return topic.matches(topicPattern);
      }).collect(Collectors.toSet());
      LOGGER.info("Topic list: {}", this.topicsToSubscribe);
      return this.consumer;
    }
  }

  protected Set<String> getTopicsToSubscribe() {
    if (this.topicsToSubscribe == null) {
      this.getConsumer();
    }

    return this.topicsToSubscribe;
  }

  public boolean isAccessible() {
    try {
      String testTopic = this.config.has("test_topic") ? this.config.get("test_topic").asText() : "";
      if (!testTopic.isBlank()) {
        KafkaConsumer<String, GenericRecord> consumer = this.getConsumer(this.topicPattern);
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

  private void close() {
    if (this.consumer != null) {
      this.consumer.close();
    }

  }

  public List<AirbyteStream> getStreams() {
    Set<String> topicsToSubscribe = getTopicsToSubscribe();
    List<AirbyteStream> streams = (List)topicsToSubscribe.stream().map((topic) -> {
      return CatalogHelpers.createAirbyteStream(topic, new Field[]{Field.of("value", JsonSchemaType.STRING)}).withSupportedSyncModes(Lists.newArrayList(new SyncMode[]{SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL}));
    }).collect(Collectors.toList());
    return streams;
  }

  private void getFromkafka() {
    this.record_index = 0;
    this.recordsList.clear();
    KafkaConsumer<String, GenericRecord> consumer =getConsumer();
    int retry = config.has("repeated_calls") ? config.get("repeated_calls").intValue() : 0;
    int polling_time = config.has("polling_time") ? config.get("polling_time").intValue() : 100;
    Map<String, Integer> poll_lookup = new HashMap();
    this.getTopicsToSubscribe().forEach((topic) -> {
      poll_lookup.put(topic, 0);
    });

    while(this.recordsList.isEmpty()) {
      ConsumerRecords<String, GenericRecord> consumerRecords = consumer.poll(Duration.of((long)polling_time, ChronoUnit.MILLIS));
      consumerRecords.forEach((record) -> {
        this.recordsList.add(record);
      });
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
          LOGGER.info("Retry details : " + poll_lookup);
          LOGGER.info("There is no new data in the queue!!");
          break;
        }
      }
    }

  }

  private ConsumerRecord<String, GenericRecord> getRecord() {
    if (this.record_index < this.recordsList.size()) {
      current_records++;
      return (ConsumerRecord)this.recordsList.get(this.record_index++);
    } else {
      if(current_records < max_records) {
        this.getFromkafka();
        return this.record_index < this.recordsList.size() ? (ConsumerRecord) this.recordsList.get(this.record_index++) : null;
      }
      else {
        return null;
      }
    }
  }

  public AutoCloseableIterator<AirbyteMessage> read(JsonNode state, List<String> topics) {
    if (!iskafkaCheckpoint() && state !=null) {
      LOGGER.info("Checkpoint restore from airbyte");
      Map<String, JsonNode> topicstate = this.convertToMap(state);
      Iterator<String> var4 = topicstate.keySet().iterator();

      while(var4.hasNext()) {
        String key = (String)var4.next();
        this.stateData.put(key, this.extractOffset((JsonNode)topicstate.get(key)));
      }
    }

    this.topicPattern = (String)topics.stream().collect(Collectors.joining("|"));
    return AutoCloseableIterators.fromIterator(this);
  }

  @CheckForNull
  protected AirbyteMessage computeNext() {
    if (this.sendstatus) {
      ConsumerRecord<String, GenericRecord> record = this.getRecord();
      if (record != null) {
        Map<Integer, Long> partition_detail = new HashMap();
        Map<Integer, Long> partitionMap = (Map)this.stateData.getOrDefault(record.topic(), partition_detail);
        partitionMap.put(record.partition(), record.offset());
        this.stateData.put(record.topic(), partitionMap);
        GenericRecord avro_data = (GenericRecord)record.value();
        ObjectMapper mapper = new ObjectMapper();
        String namespace = avro_data.getSchema().getNamespace();
        String name = avro_data.getSchema().getName();

        JsonNode output;
        try {
          String partitionInfo;
          JsonNode partitionNode;
          if (StringUtils.isNoneEmpty(new CharSequence[]{namespace}) && StringUtils.isNoneEmpty(new CharSequence[]{name})) {
            partitionInfo = String.format("{\"avro_schema\": \"%s\",\"name\":\"%s\"}", namespace, name);
            partitionNode = mapper.readTree(partitionInfo);
            output = mapper.readTree(avro_data.toString());
            ((ObjectNode)output).set("_namespace_", partitionNode);
          } else {
            output = mapper.readTree(avro_data.toString());
          }

          partitionInfo = String.format("{\"partition\": \"%s\",\"offset\":\"%s\"}", record.partition(), record.offset());
          partitionNode = mapper.readTree(partitionInfo);
          ((ObjectNode)output).set("_partitioninfo_", partitionNode);
        } catch (JsonProcessingException var11) {
          LOGGER.error("Exception whilst reading avro data from stream", var11);
          throw new RuntimeException(var11);
        }

        return (new AirbyteMessage()).withType(AirbyteMessage.Type.RECORD).withRecord((new AirbyteRecordMessage()).withStream(record.topic()).withEmittedAt(Instant.now().toEpochMilli()).withData(output));
      }

      if (iskafkaCheckpoint()) {
        this.sendstatus = false;
        LOGGER.info("sending the status: " + this.stateData);
        LOGGER.info("closing the connection !!");
        return (new AirbyteMessage()).withType(AirbyteMessage.Type.STATE).withState((new AirbyteStateMessage()).withData(Jsons.jsonNode(this.stateData)));
      }else {
        LOGGER.info("commit to kafka");
        this.consumer.commitAsync();
      }
    }

    this.close();
    return (AirbyteMessage)this.endOfData();
  }
}
