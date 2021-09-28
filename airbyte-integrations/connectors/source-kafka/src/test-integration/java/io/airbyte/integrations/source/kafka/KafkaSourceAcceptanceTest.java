/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.*;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.utility.DockerImageName;

public class KafkaSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();
  private static final String TOPIC_NAME = "test.topic";

  private static KafkaContainer KAFKA;

  @Override
  protected String getImageName() {
    return "airbyte/source-kafka:dev";
  }

  @Override
  protected JsonNode getConfig() {
    ObjectNode stubProtocolConfig = mapper.createObjectNode();
    stubProtocolConfig.put("security_protocol", KafkaProtocol.PLAINTEXT.toString());

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("bootstrap_servers", KAFKA.getBootstrapServers())
        .put("topic_pattern", TOPIC_NAME)
        .build());
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    KAFKA = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:6.2.0"));
    KAFKA.start();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    KAFKA.close();
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
    return CatalogHelpers.createConfiguredAirbyteCatalog(
        TOPIC_NAME,
        null,
        Field.of("value", JsonSchemaPrimitive.STRING));
  }

  @Override
  protected JsonNode getState() throws Exception {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected List<String> getRegexTests() throws Exception {
    return Collections.emptyList();
  }

}
