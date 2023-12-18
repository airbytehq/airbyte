/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;

public class CassandraDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private JsonNode configJson;

  private CassandraCqlProvider cassandraCqlProvider;

  private CassandraNameTransformer cassandraNameTransformer;

  private static CassandraContainerInitializr.ConfiguredCassandraContainer cassandraContainer;

  @BeforeAll
  static void initContainer() {
    cassandraContainer = CassandraContainerInitializr.initContainer();
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    configJson = TestDataFactory.createJsonConfig(
        cassandraContainer.getUsername(),
        cassandraContainer.getPassword(),
        HostPortResolver.resolveHost(cassandraContainer),
        HostPortResolver.resolvePort(cassandraContainer));
    final var cassandraConfig = new CassandraConfig(configJson);
    cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig);
    cassandraNameTransformer = new CassandraNameTransformer(cassandraConfig);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    cassandraCqlProvider.retrieveMetadata().forEach(meta -> {
      final var keyspace = meta.value1();
      meta.value2().forEach(table -> cassandraCqlProvider.truncate(keyspace, table));
    });
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-cassandra:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return TestDataFactory.createJsonConfig(
        "usr",
        "pw",
        "127.0.192.1",
        8080);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final var keyspace = cassandraNameTransformer.outputKeyspace(namespace);
    final var table = cassandraNameTransformer.outputTable(streamName);
    return cassandraCqlProvider.select(keyspace, table).stream()
        .sorted(Comparator.comparing(CassandraRecord::getTimestamp))
        .map(CassandraRecord::getData)
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

}
