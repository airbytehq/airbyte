/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import com.exasol.containers.ExasolContainer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;

public class ExasolDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(ExasolDestinationAcceptanceTest.class);

  private static final ExasolContainer<? extends ExasolContainer<?>> EXASOL = new ExasolContainer<>().withReuse(true);

  private final NamingConventionTransformer namingResolver = new ExasolSQLNameTransformer();

  @BeforeAll
  static void startExasolContainer() throws IOException {
    Files.createDirectories(Path.of("target"));
    EXASOL.start();
  }

  @AfterAll
  static void stopExasolContainer() {
    EXASOL.stop();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-exasol:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
            .put("connectionstring",EXASOL.getHost()+"/"+EXASOL.getTlsCertificateFingerprint().orElseThrow()+":"+EXASOL.getFirstMappedDatabasePort())
            .put(JdbcUtils.USERNAME_KEY, EXASOL.getUsername())
            .put(JdbcUtils.PASSWORD_KEY, EXASOL.getPassword())
            .put(JdbcUtils.SCHEMA_KEY, "TEST")
            .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put(JdbcUtils.PASSWORD_KEY, "wrong password");
    return clone;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema) throws SQLException {
    return retrieveRecordsFromTable(namingResolver.getIdentifier(streamName), "\"_"+namespace+"_\"")
            .stream()
            .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase()))
            .map(node -> Jsons.deserialize(node.asText()))
            .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    final JdbcDatabase jdbcDB = getDatabase(getConfig());
    final String query = String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, ExasolSqlOperations.COLUMN_NAME_EMITTED_AT);
    return jdbcDB.queryJsons(query);
  }

  private static JdbcDatabase getDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
            DataSourceFactory.create(
                    config.get(JdbcUtils.USERNAME_KEY).asText(),
                    config.has(JdbcUtils.PASSWORD_KEY) ? config.get(JdbcUtils.PASSWORD_KEY).asText() : null,
                    ExasolDestination.DRIVER_CLASS,
                    String.format(DatabaseDriver.EXASOL.getUrlFormatString(), config.get("connectionstring").asText()))
    );
  }

  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    // Nothing to do
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    EXASOL.purgeDatabase();
  }
}
