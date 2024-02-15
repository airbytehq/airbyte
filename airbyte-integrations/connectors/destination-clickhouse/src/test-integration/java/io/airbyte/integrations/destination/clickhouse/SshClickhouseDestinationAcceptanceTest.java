/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.testcontainers.containers.ClickHouseContainer;
import org.testcontainers.containers.Network;

/**
 * Abstract class that allows us to avoid duplicating testing logic for testing SSH with a key file
 * or with a password.
 */
public abstract class SshClickhouseDestinationAcceptanceTest extends DestinationAcceptanceTest {

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  private static final String DB_NAME = "default";
  private static final Network network = Network.newNetwork();

  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

  private ClickHouseContainer db;
  private final SshBastionContainer bastion = new SshBastionContainer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-clickhouse:dev";
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new ClickhouseTestDataComparator();
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
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get(JdbcUtils.DATABASE_KEY) == null) {
      return null;
    }
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), bastion.getBasicDbConfigBuider(db, DB_NAME)
        .put("schema", DB_NAME), true);
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv,
                                                     final String streamName,
                                                     final String namespace)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getIdentifier(streamName), namespace);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(StreamId.concatenateRawTableName(namespace, streamName), "airbyte_internal")
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
    return SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        mangledConfig -> {
          final JdbcDatabase database = getDatabase(mangledConfig);
          final String query = String.format("SELECT * FROM `%s`.`%s` ORDER BY %s ASC", schemaName, namingResolver.convertStreamName(tableName),
              JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT);
          return database.queryJsons(query);
        });
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
      result.add(resolved.toUpperCase());
    }
    return result;
  }

  private static JdbcDatabase getDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.has(JdbcUtils.PASSWORD_KEY) ? config.get(JdbcUtils.PASSWORD_KEY).asText() : null,
            ClickhouseDestination.DRIVER_CLASS,
            String.format(DatabaseDriver.CLICKHOUSE.getUrlFormatString(),
                ClickhouseDestination.HTTP_PROTOCOL,
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText())),
        new ClickhouseTestSourceOperations());
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    bastion.initAndStartBastion(network);
    db = (ClickHouseContainer) new ClickHouseContainer("clickhouse/clickhouse-server:22.5").withNetwork(network);
    db.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
  }

  @ParameterizedTest
  @ArgumentsSource(DataTypeTestArgumentProvider.class)
  public void testDataTypeTestWithNormalization(final String messagesFilename,
                                                final String catalogFilename,
                                                final DataTypeTestArgumentProvider.TestCompatibility testCompatibility)
      throws Exception {

    // arrays are not fully supported yet in jdbc driver
    // https://github.com/ClickHouse/clickhouse-jdbc/blob/master/clickhouse-jdbc/src/main/java/ru/yandex/clickhouse/ClickHouseArray.java
    if (messagesFilename.contains("array")) {
      return;
    }

    super.testDataTypeTestWithNormalization(messagesFilename, catalogFilename, testCompatibility);
  }

}
