package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.integrations.util.HostPortResolver;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.apache.commons.io.IOUtils;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.connect.json.JsonDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.BindMode;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.utility.DockerImageName;

public class KafkaSslDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(KafkaSslDestinationAcceptanceTest.class);
  private static final ObjectMapper mapper = MoreMappers.initMapper();
  private static final String TOPIC_NAME = "test.topic";

  private static KafkaContainer KAFKA;

  private final NamingConventionTransformer namingResolver = new StandardNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-kafka:dev";
  }

  @Override
  protected JsonNode getConfig() throws IOException {
    // This file is generated inside create_certs.sh
    String truststoreCertificates = KAFKA.copyFileFromContainer(
        "/etc/kafka/secrets/kafka.producer.truststore.pem",
        is -> IOUtils.toString(is, StandardCharsets.UTF_8));
    JsonNode stubProtocolConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("truststore_certificates", truststoreCertificates)
        .put("security_protocol", "SSL")
        .build());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", HostPortResolver.resolveHost(KAFKA) + ":" + HostPortResolver.resolvePort(KAFKA))
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("sync_producer", true)
        .put("protocol", stubProtocolConfig)
        .put("client_id", "test-client")
        .put("acks", "all")
        .put("enable_idempotence", true)
        .put("compression_type", "none")
        .put("batch_size", 16384)
        .put("linger_ms", "0")
        .put("max_in_flight_requests_per_connection", 5)
        .put("client_dns_lookup", "use_all_dns_ips")
        .put("buffer_memory", "33554432")
        .put("max_request_size", 1048576)
        .put("retries", 2147483647)
        .put("socket_connection_setup_timeout_ms", "10000")
        .put("socket_connection_setup_timeout_max_ms", "30000")
        .put("max_block_ms", "60000")
        .put("request_timeout_ms", 30000)
        .put("delivery_timeout_ms", 120000)
        .put("send_buffer_bytes", -1)
        .put("receive_buffer_bytes", -1)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final ObjectNode stubProtocolConfig = mapper.createObjectNode();
    stubProtocolConfig.put("security_protocol", KafkaProtocol.SASL_PLAINTEXT.toString());
    stubProtocolConfig.put("sasl_mechanism", "PLAIN");
    stubProtocolConfig.put("sasl_jaas_config", "invalid");

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", KAFKA.getBootstrapServers())
        .put("topic_pattern", "{namespace}.{stream}." + TOPIC_NAME)
        .put("test_topic", "check-topic")
        .put("protocol", stubProtocolConfig)
        .put("client_id", "test-client")
        .put("acks", "all")
        .put("enable_idempotence", true)
        .put("compression_type", "none")
        .put("batch_size", 16384)
        .put("linger_ms", 0)
        .put("max_in_flight_requests_per_connection", 5)
        .put("client_dns_lookup", "use_all_dns_ips")
        .put("buffer_memory", 33554432)
        .put("max_request_size", 1048576)
        .put("retries", 2147483647)
        .put("socket_connection_setup_timeout_ms", 10000)
        .put("socket_connection_setup_timeout_max_ms", 30000)
        .put("max_block_ms", 60000)
        .put("request_timeout_ms", 30000)
        .put("delivery_timeout_ms", 120000)
        .put("send_buffer_bytes", -1)
        .put("receive_buffer_bytes", -1)
        .build());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    return "";
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace) {
    return retrieveRecords(testEnv, streamName, namespace, null);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final Map<String, Object> props = ImmutableMap.<String, Object>builder()
        .put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, KAFKA.getBootstrapServers())
        .put(ConsumerConfig.GROUP_ID_CONFIG, namingResolver.getIdentifier(namespace + "-" + streamName))
        .put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest")
        .put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName())
        .put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class.getName())
        .build();
    final KafkaConsumer<String, JsonNode> consumer = new KafkaConsumer<>(props);
    final List<JsonNode> records = new ArrayList<>();
    final String topic = namingResolver.getIdentifier(namespace + "." + streamName + "." + TOPIC_NAME);

    consumer.subscribe(Collections.singletonList(topic));
    consumer.poll(Duration.ofMillis(20000L)).iterator()
        .forEachRemaining(record -> records.add(record.value().get(JavaBaseConstants.COLUMN_NAME_DATA)));
    consumer.close();

    return records;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    KAFKA = new SslKafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:6.2.0"))
        .withEnv(Map.of(
            "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP", "SSL:SSL,BROKER:PLAINTEXT",
            // Note that the testcontainer will remap advertised.listeners to actual ports/IPs
            // So the actual advertised listeners will be something like "SSL://localhost:55160,BROKER://172.17.0.3:9092"
            "KAFKA_LISTENERS", "SSL://0.0.0.0:9093,BROKER://0.0.0.0:9092",
            "KAFKA_SSL_KEYSTORE_FILENAME", "kafka.broker1.keystore.jks",
            "KAFKA_SSL_KEYSTORE_CREDENTIALS", "broker1_keystore_creds",
            "KAFKA_SSL_KEY_CREDENTIALS", "broker1_sslkey_creds"
        ))
    ;
    KAFKA.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    KAFKA.close();
  }

}
