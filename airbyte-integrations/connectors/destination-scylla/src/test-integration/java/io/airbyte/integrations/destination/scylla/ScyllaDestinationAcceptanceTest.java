/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.scylla.ScyllaContainerInitializr.ScyllaContainer;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;

class ScyllaDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private JsonNode configJson;

  private ScyllaCqlProvider scyllaCqlProvider;

  private ScyllaNameTransformer nameTransformer;

  private static ScyllaContainer scyllaContainer;

  @Override
  protected String getImageName() {
    return "airbyte/destination-scylla:dev";
  }

  @BeforeAll
  static void initContainer() {
    scyllaContainer = ScyllaContainerInitializr.initContainer();
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    configJson = TestDataFactory.jsonConfig(
        HostPortResolver.resolveHost(scyllaContainer),
        HostPortResolver.resolvePort(scyllaContainer));
    final var scyllaConfig = new ScyllaConfig(configJson);
    this.scyllaCqlProvider = new ScyllaCqlProvider(scyllaConfig);
    this.nameTransformer = new ScyllaNameTransformer(scyllaConfig);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    scyllaCqlProvider.metadata().stream()
        .filter(m -> !m.value1().startsWith("system"))
        .forEach(meta -> {
          final var keyspace = meta.value1();
          meta.value2().forEach(table -> scyllaCqlProvider.truncate(keyspace, table));
        });
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return TestDataFactory.jsonConfig("127.129.0.1", 8080);
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
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
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final var keyspace = nameTransformer.outputKeyspace(namespace);
    final var table = nameTransformer.outputTable(streamName);
    return scyllaCqlProvider.select(keyspace, table).stream()
        .sorted(Comparator.comparing(Triplet::value3))
        .map(Triplet::value2)
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

}
