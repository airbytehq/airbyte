/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import static java.time.temporal.ChronoUnit.SECONDS;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.BindMode;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.images.builder.ImageFromDockerfile;

public class ClickhouseDestinationStrictEncryptAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseDestinationStrictEncryptAcceptanceTest.class);

  public static final Integer HTTP_PORT = 8123;
  public static final Integer NATIVE_PORT = 9000;
  public static final Integer HTTPS_PORT = 8443;
  public static final Integer NATIVE_SECURE_PORT = 9440;
  private static final String DB_NAME = "default";
  private static final String USER_NAME = "default";
  private final StandardNameTransformer namingResolver = new StandardNameTransformer();
  private GenericContainer db;

  private static JdbcDatabase getDatabase(final JsonNode config) {
    final String jdbcStr = String.format(DatabaseDriver.CLICKHOUSE.getUrlFormatString() + "?sslmode=NONE",
        ClickhouseDestination.HTTPS_PROTOCOL,
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asInt(),
        config.get(JdbcUtils.DATABASE_KEY).asText());
    return new DefaultJdbcDatabase(DataSourceFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.has(JdbcUtils.PASSWORD_KEY) ? config.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        ClickhouseDestination.DRIVER_CLASS,
        jdbcStr), new ClickhouseTestSourceOperations());
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-clickhouse-strict-encrypt:dev";
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
  protected String getDestinationDefinitionKey() {
    return "airbyte/destination-clickhouse";
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get(JdbcUtils.DATABASE_KEY) == null) {
      return null;
    }
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveIpAddress(db))
        .put(JdbcUtils.PORT_KEY, HTTPS_PORT)
        .put(JdbcUtils.DATABASE_KEY, DB_NAME)
        .put(JdbcUtils.USERNAME_KEY, USER_NAME)
        .put(JdbcUtils.PASSWORD_KEY, "")
        .put(JdbcUtils.SCHEMA_KEY, DB_NAME)
        .put(JdbcUtils.SSL_KEY, true)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password").put(JdbcUtils.SSL_KEY, false);
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

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    final JdbcDatabase jdbcDB = getDatabase(getConfig());
    final var nameTransformer = new StandardNameTransformer();
    final String query = String.format("SELECT * FROM `%s`.`%s` ORDER BY %s ASC", schemaName, nameTransformer.convertStreamName(tableName),
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT);
    return jdbcDB.queryJsons(query);
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

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    db = new GenericContainer<>(new ImageFromDockerfile("clickhouse-test")
        .withFileFromClasspath("Dockerfile", "docker/Dockerfile")
        .withFileFromClasspath("clickhouse_certs.sh", "docker/clickhouse_certs.sh"))
            .withEnv("TZ", "UTC")
            .withExposedPorts(HTTP_PORT, NATIVE_PORT, HTTPS_PORT, NATIVE_SECURE_PORT)
            .withClasspathResourceMapping("ssl_ports.xml", "/etc/clickhouse-server/config.d/ssl_ports.xml", BindMode.READ_ONLY)
            .waitingFor(Wait.forHttp("/ping").forPort(HTTP_PORT)
                .forStatusCode(200).withStartupTimeout(Duration.of(60, SECONDS)));

    db.start();

    LOGGER.info(String.format("Clickhouse server container port mapping: %d -> %d, %d -> %d, %d -> %d, %d -> %d",
        HTTP_PORT, db.getMappedPort(HTTP_PORT),
        HTTPS_PORT, db.getMappedPort(HTTPS_PORT),
        NATIVE_PORT, db.getMappedPort(NATIVE_PORT),
        NATIVE_SECURE_PORT, db.getMappedPort(NATIVE_SECURE_PORT)));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  @Override
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
