/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.cdk.db.factory.DSLContextFactory.create;
import static io.airbyte.cdk.db.jdbc.JdbcUtils.getDefaultJSONFormat;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static io.airbyte.cdk.integrations.destination.s3.util.AvroRecordHelper.pruneAirbyteJson;
import static io.airbyte.commons.json.Jsons.deserialize;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyBaseDestination.getGalaxyConnectionString;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.STARBURST_GALAXY_DRIVER_CLASS;
import static io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD;
import static io.airbyte.protocol.models.v0.DestinationSyncMode.APPEND;
import static io.airbyte.protocol.models.v0.DestinationSyncMode.OVERWRITE;
import static io.airbyte.protocol.models.v0.SyncMode.FULL_REFRESH;
import static java.lang.String.format;
import static java.nio.file.Files.readString;
import static java.util.Locale.ENGLISH;
import static java.util.stream.Collectors.toList;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.field;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.ContextQueryFunction;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.cdk.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.cdk.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class StarburstGalaxyDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(StarburstGalaxyDestinationAcceptanceTest.class);
  private static final String INPUT_FILES_BASE_LOCATION = "testdata/";
  private static final StandardNameTransformer nameTransformer = new StarburstGalaxyNameTransformer();

  protected JsonNode configJson;
  protected StarburstGalaxyDestinationConfig galaxyDestinationConfig;
  private DSLContext dslContext;
  private Database database;

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    dslContext = create(galaxyDestinationConfig.galaxyUsername(), galaxyDestinationConfig.galaxyPassword(), STARBURST_GALAXY_DRIVER_CLASS,
        getGalaxyConnectionString(galaxyDestinationConfig), SQLDialect.DEFAULT);
    database = new Database(dslContext);
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-starburst-galaxy:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws SQLException {
    final String tableName = nameTransformer.getIdentifier(streamName);
    final String schemaName = StreamCopierFactory.getSchema(namespace, galaxyDestinationConfig.galaxyCatalogSchema(), nameTransformer);
    final JsonFieldNameUpdater nameUpdater = AvroRecordHelper.getFieldNameUpdater(streamName, namespace, streamSchema);
    return executeQuery(
        ctx -> ctx.select(asterisk())
            .from(format("%s.%s", schemaName, tableName))
            .orderBy(field(COLUMN_NAME_EMITTED_AT).asc())
            .fetch().stream()
            .map(record -> {
              final JsonNode json = deserialize(record.formatJSON(getDefaultJSONFormat()));
              final JsonNode jsonWithOriginalFields = nameUpdater.getJsonWithOriginalFieldNames(json);
              return pruneAirbyteJson(jsonWithOriginalFields);
            })
            .collect(toList()));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    // clean up database
    final List<JsonNode> schemas = executeQuery(format("SHOW SCHEMAS LIKE '%s'", galaxyDestinationConfig.galaxyCatalogSchema().toLowerCase(ENGLISH)));
    schemas.stream().map(node -> node.get("Schema").asText())
        .forEach(schema -> {
          try {
            final List<JsonNode> tables = executeQuery(format("SHOW TABLES FROM %s", galaxyDestinationConfig.galaxyCatalogSchema()));
            tables.forEach(table -> {
              try {
                final String tableName = table.get("Table").asText();
                LOGGER.info("Dropping table : {}.{}", schema, tableName);
                executeQuery(format("DROP TABLE IF EXISTS %s.%s", schema, tableName));
              } catch (final SQLException e) {
                throw new RuntimeException(e);
              }
            });
          } catch (final SQLException e) {
            throw new RuntimeException(e);
          }
        });
    executeQuery(format("DROP SCHEMA IF EXISTS %s", galaxyDestinationConfig.galaxyCatalogSchema().toLowerCase(ENGLISH)));

    dslContext.close();
  }

  private List<JsonNode> executeQuery(final ContextQueryFunction<List<JsonNode>> transform)
      throws SQLException {
    return database.query(transform);
  }

  private List<JsonNode> executeQuery(final String query)
      throws SQLException {
    return executeQuery(ctx -> ctx.resultQuery(query)
        .stream()
        .map(record -> deserialize(record.formatJSON(getDefaultJSONFormat())))
        .collect(toList()));
  }

  @Test
  public void testPromoteSourceSchemaChanges() throws Exception {
    final String sampleStream = "sample_stream_1";
    testStreamSync(OVERWRITE, sampleStream, "schema-overwrite.json", "data-overwrite.json", "expected-schema-overwrite.json");
    testStreamSync(APPEND, sampleStream, "schema-append.json", "data-append.json", "expected-schema-append.json");
    assertEquals(2,
        executeQuery(format("SELECT COUNT(*) FROM %s.%s", galaxyDestinationConfig.galaxyCatalogSchema(), sampleStream)).get(0).get("_col0").asInt());
  }

  private void testStreamSync(final DestinationSyncMode syncMode,
                              final String streamName,
                              final String schemaFileName,
                              final String dataFileName,
                              final String expectedSchemaFileName)
      throws Exception {
    final JsonNode overwriteSchema = getTestDataFromResourceJson(schemaFileName);
    final AirbyteMessage overwriteMessage = createRecordMessage(streamName, getTestDataFromResourceJson(dataFileName));
    runDestinationWrite(getCommonCatalog(streamName, overwriteSchema, syncMode), configJson, overwriteMessage);
    validateTableSchema(streamName, expectedSchemaFileName);
  }

  private void validateTableSchema(final String streamName, final String expectedSchemaFileName)
      throws SQLException {
    final List<JsonNode> describeRecords = executeQuery(format("DESCRIBE %s.%s", galaxyDestinationConfig.galaxyCatalogSchema(), streamName));
    final Map<String, String> actualDataTypes =
        describeRecords.stream().collect(Collectors.toMap(column -> column.get("Column").asText(), column -> column.get("Type").asText()));
    final JsonNode expectedDataTypes = getTestDataFromResourceJson(expectedSchemaFileName);
    assertEquals(expectedDataTypes.size(), actualDataTypes.size());
    expectedDataTypes.fields().forEachRemaining(field -> assertEquals(field.getValue().asText(), actualDataTypes.get(field.getKey())));
  }

  @Test
  public void testJsonV0Types() throws Exception {
    testDifferentTypes("sample_stream_2", "datatypeV0.json", "dataV0.json", "expected-datatypeV0.json", "expected-dataV0.json");
  }

  @Test
  public void testJsonV1Types() throws Exception {
    testDifferentTypes("sample_stream_3", "datatypeV1.json", "dataV1.json", "expected-datatypeV1.json", "expected-dataV1.json");
  }

  private void testDifferentTypes(final String streamName,
                                  final String dataTypeFile,
                                  final String dataFile,
                                  final String expectedDataTypeFile,
                                  final String expectedDataFile)
      throws Exception {

    final JsonNode datatypeSchema = getTestDataFromResourceJson(dataTypeFile);
    final AirbyteMessage datatypeMessage = createRecordMessage(streamName, getTestDataFromResourceJson(dataFile));
    runDestinationWrite(getCommonCatalog(streamName, datatypeSchema, OVERWRITE), configJson, datatypeMessage);
    final JsonFieldNameUpdater nameUpdater =
        AvroRecordHelper.getFieldNameUpdater(streamName, galaxyDestinationConfig.galaxyCatalogSchema(), datatypeSchema);
    validateTableSchema(streamName, expectedDataTypeFile);

    final List<JsonNode> records = executeQuery(ctx -> ctx.select(asterisk())
        .from(format("%s.%s", galaxyDestinationConfig.galaxyCatalogSchema(), streamName))
        .orderBy(field(COLUMN_NAME_EMITTED_AT).asc())
        .fetch().stream()
        .map(record -> {
          final JsonNode json = deserialize(record.formatJSON(getDefaultJSONFormat()));
          final JsonNode jsonWithOriginalFields = nameUpdater.getJsonWithOriginalFieldNames(json);
          return pruneAirbyteJson(jsonWithOriginalFields);
        })
        .collect(toList()));
    final JsonNode actualData = records.get(0);
    final JsonNode expectedData = getTestDataFromResourceJson(expectedDataFile);
    assertEquals(expectedData.size(), actualData.size());
    expectedData.fields().forEachRemaining(field -> assertEquals(field.getValue(), actualData.get(field.getKey())));
  }

  private static AirbyteMessage createRecordMessage(final String streamName, final JsonNode data) {
    return new AirbyteMessage()
        .withType(RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withData(data).withEmittedAt(Instant.now().toEpochMilli()));
  }

  public static ConfiguredAirbyteCatalog getCommonCatalog(final String stream, final JsonNode schema, final DestinationSyncMode destinationSyncMode) {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(stream).withJsonSchema(schema)
            .withSupportedSyncModes(Lists.newArrayList(FULL_REFRESH)))
        .withSyncMode(FULL_REFRESH).withDestinationSyncMode(destinationSyncMode)));
  }

  private static void runDestinationWrite(final ConfiguredAirbyteCatalog catalog, final JsonNode config, final AirbyteMessage... messages)
      throws Exception {
    final StarburstGalaxyDestination destination = new StarburstGalaxyDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);
    consumer.start();
    for (final AirbyteMessage message : messages) {
      consumer.accept(message);
    }
    consumer.close();
  }

  private static JsonNode getTestDataFromResourceJson(final String fileName) {
    try {
      final String fileContent = readString(Path.of(Objects.requireNonNull(StarburstGalaxyDestinationAcceptanceTest.class.getClassLoader()
          .getResource(INPUT_FILES_BASE_LOCATION + fileName)).getPath()));
      return Jsons.deserialize(fileContent);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

}
