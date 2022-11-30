/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mqtt;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectReader;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Streams;
import com.google.common.net.InetAddresses;
import com.hivemq.testcontainer.junit5.HiveMQTestContainerExtension;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.testcontainers.utility.DockerImageName;

public class MqttDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final String TOPIC_PREFIX = "test/integration/";
  private static final String TOPIC_NAME = "test.topic";
  private static final ObjectReader READER = new ObjectMapper().reader();

  private final Map<String, List<JsonNode>> recordsPerTopic = new HashMap<>();
  private MqttClient client;

  @RegisterExtension
  public final HiveMQTestContainerExtension extension = new HiveMQTestContainerExtension(DockerImageName.parse("hivemq/hivemq-ce:2021.2"));

  @Override
  protected String getImageName() {
    return "airbyte/destination-mqtt:dev";
  }

  @Override
  protected JsonNode getConfig() throws UnknownHostException {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("broker_host", getIpAddress())
        .put("broker_port", extension.getMqttPort())
        .put("use_tls", false)
        .put("topic_pattern", TOPIC_PREFIX + "{namespace}/{stream}/" + TOPIC_NAME)
        .put("client_id", UUID.randomUUID())
        .put("publisher_sync", true)
        .put("connect_timeout", 10)
        .put("automatic_reconnect", true)
        .put("clean_session", true)
        .put("message_retained", false)
        .put("message_qos", "EXACTLY_ONCE")
        .put("max_in_flight", 1000)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("broker_host", extension.getHost())
        .put("broker_port", extension.getMqttPort())
        .put("topic_pattern", TOPIC_PREFIX + "{namespace}/{stream}/" + TOPIC_NAME)
        .put("client_id", UUID.randomUUID())
        .put("publisher_sync", true)
        .put("connect_timeout", 10)
        .put("automatic_reconnect", true)
        .build());
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
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
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    return "";
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
    final String topic = TOPIC_PREFIX + namespace + "/" + streamName + "/" + TOPIC_NAME;
    return recordsPerTopic.getOrDefault(topic, Collections.emptyList());
  }

  @SuppressWarnings("UnstableApiUsage")
  private String getIpAddress() throws UnknownHostException {
    try {
      return Streams.stream(NetworkInterface.getNetworkInterfaces().asIterator())
          .flatMap(ni -> Streams.stream(ni.getInetAddresses().asIterator()))
          .filter(add -> !add.isLoopbackAddress())
          .map(InetAddress::getHostAddress)
          .filter(InetAddresses::isUriInetAddress)
          .findFirst().orElse(InetAddress.getLocalHost().getHostAddress());
    } catch (SocketException e) {
      return InetAddress.getLocalHost().getHostAddress();
    }
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws MqttException {
    recordsPerTopic.clear();
    client = new MqttClient("tcp://" + extension.getHost() + ":" + extension.getMqttPort(), UUID.randomUUID().toString(), new MemoryPersistence());

    final MqttConnectOptions options = new MqttConnectOptions();
    options.setAutomaticReconnect(true);

    client.connect(options);

    client.subscribe(TOPIC_PREFIX + "#", (topic, msg) -> {
      List<JsonNode> records = recordsPerTopic.getOrDefault(topic, new ArrayList<>());
      records.add(READER.readTree(msg.getPayload()).get(MqttDestination.COLUMN_NAME_DATA));
      recordsPerTopic.put(topic, records);
    });
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws MqttException {
    client.disconnectForcibly();
    client.close();
  }

}
