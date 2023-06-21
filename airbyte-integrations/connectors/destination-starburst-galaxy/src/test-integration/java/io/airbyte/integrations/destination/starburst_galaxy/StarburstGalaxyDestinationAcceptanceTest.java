/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.commons.json.Jsons.deserialize;
import static io.airbyte.db.factory.DSLContextFactory.create;
import static io.airbyte.db.jdbc.JdbcUtils.getDefaultJSONFormat;
import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static io.airbyte.integrations.destination.s3.util.AvroRecordHelper.pruneAirbyteJson;
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
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.ContextQueryFunction;
import io.airbyte.db.Database;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
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
  protected void setup(TestDestinationEnv testEnv) {
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
    List<JsonNode> schemas = executeQuery(format("SHOW SCHEMAS LIKE '%s'", galaxyDestinationConfig.galaxyCatalogSchema().toLowerCase(ENGLISH)));
    schemas.stream().map(node -> node.get("Schema").asText())
        .forEach(schema -> {
          try {
            List<JsonNode> tables = executeQuery(format("SHOW TABLES FROM %s", galaxyDestinationConfig.galaxyCatalogSchema()));
            tables.forEach(table -> {
              try {
                String tableName = table.get("Table").asText();
                LOGGER.info("Dropping table : {}.{}", schema, tableName);
                executeQuery(format("DROP TABLE IF EXISTS %s.%s", schema, tableName));
              } catch (SQLException e) {
                throw new RuntimeException(e);
              }
            });
          } catch (SQLException e) {
            throw new RuntimeException(e);
          }
        });
    executeQuery(format("DROP SCHEMA IF EXISTS %s", galaxyDestinationConfig.galaxyCatalogSchema().toLowerCase(ENGLISH)));

    dslContext.close();
  }

  private List<JsonNode> executeQuery(ContextQueryFunction<List<JsonNode>> transform)
      throws SQLException {
    return database.query(transform);
  }

  private List<JsonNode> executeQuery(String query)
      throws SQLException {
    return executeQuery(ctx -> ctx.resultQuery(query)
        .stream()
        .map(record -> deserialize(record.formatJSON(getDefaultJSONFormat())))
        .collect(toList()));
  }

  @Test
  public void testPromoteSourceSchemaChanges() throws Exception {
    String sampleStream = "sample_stream_1";
    testStreamSync(OVERWRITE, sampleStream, "schema-overwrite.json", "data-overwrite.json", "expected-schema-overwrite.json");
    testStreamSync(APPEND, sampleStream, "schema-append.json", "data-append.json", "expected-schema-append.json");
    assertEquals(2,
        executeQuery(format("SELECT COUNT(*) FROM %s.%s", galaxyDestinationConfig.galaxyCatalogSchema(), sampleStream)).get(0).get("_col0").asInt());
  }

  private void testStreamSync(DestinationSyncMode syncMode,
                              String streamName,
                              String schemaFileName,
                              String dataFileName,
                              String expectedSchemaFileName)
      throws Exception {
    JsonNode overwriteSchema = getTestDataFromResourceJson(schemaFileName);
    AirbyteMessage overwriteMessage = createRecordMessage(streamName, getTestDataFromResourceJson(dataFileName));
    runDestinationWrite(getCommonCatalog(streamName, overwriteSchema, syncMode), configJson, overwriteMessage);
    validateTableSchema(streamName, expectedSchemaFileName);
  }

  private void validateTableSchema(String streamName, String expectedSchemaFileName)
      throws SQLException {
    List<JsonNode> describeRecords = executeQuery(format("DESCRIBE %s.%s", galaxyDestinationConfig.galaxyCatalogSchema(), streamName));
    Map<String, String> actualDataTypes =
        describeRecords.stream().collect(Collectors.toMap(column -> column.get("Column").asText(), column -> column.get("Type").asText()));
    JsonNode expectedDataTypes = getTestDataFromResourceJson(expectedSchemaFileName);
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

  private void testDifferentTypes(String streamName, String dataTypeFile, String dataFile, String expectedDataTypeFile, String expectedDataFile)
      throws Exception {

    JsonNode datatypeSchema = getTestDataFromResourceJson(dataTypeFile);
    AirbyteMessage datatypeMessage = createRecordMessage(streamName, getTestDataFromResourceJson(dataFile));
    runDestinationWrite(getCommonCatalog(streamName, datatypeSchema, OVERWRITE), configJson, datatypeMessage);
    final JsonFieldNameUpdater nameUpdater =
        AvroRecordHelper.getFieldNameUpdater(streamName, galaxyDestinationConfig.galaxyCatalogSchema(), datatypeSchema);
    validateTableSchema(streamName, expectedDataTypeFile);

    List<JsonNode> records = executeQuery(ctx -> ctx.select(asterisk())
        .from(format("%s.%s", galaxyDestinationConfig.galaxyCatalogSchema(), streamName))
        .orderBy(field(COLUMN_NAME_EMITTED_AT).asc())
        .fetch().stream()
        .map(record -> {
          final JsonNode json = deserialize(record.formatJSON(getDefaultJSONFormat()));
          final JsonNode jsonWithOriginalFields = nameUpdater.getJsonWithOriginalFieldNames(json);
          return pruneAirbyteJson(jsonWithOriginalFields);
        })
        .collect(toList()));
    JsonNode actualData = records.get(0);
    JsonNode expectedData = getTestDataFromResourceJson(expectedDataFile);
    assertEquals(expectedData.size(), actualData.size());
    expectedData.fields().forEachRemaining(field -> assertEquals(field.getValue(), actualData.get(field.getKey())));
  }

  private static AirbyteMessage createRecordMessage(String streamName, final JsonNode data) {
    return new AirbyteMessage()
        .withType(RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withData(data).withEmittedAt(Instant.now().toEpochMilli()));
  }

  public static ConfiguredAirbyteCatalog getCommonCatalog(String stream, final JsonNode schema, DestinationSyncMode destinationSyncMode) {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(stream).withJsonSchema(schema)
            .withSupportedSyncModes(Lists.newArrayList(FULL_REFRESH)))
        .withSyncMode(FULL_REFRESH).withDestinationSyncMode(destinationSyncMode)));
  }

  private static void runDestinationWrite(ConfiguredAirbyteCatalog catalog, JsonNode config, AirbyteMessage... messages) throws Exception {
    final StarburstGalaxyDestination destination = new StarburstGalaxyDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);
    consumer.start();
    for (AirbyteMessage message : messages) {
      consumer.accept(message);
    }
    consumer.close();
  }

  private static JsonNode getTestDataFromResourceJson(final String fileName) {
    try {
      String fileContent = readString(Path.of(Objects.requireNonNull(StarburstGalaxyDestinationAcceptanceTest.class.getClassLoader()
          .getResource(INPUT_FILES_BASE_LOCATION + fileName)).getPath()));
      return Jsons.deserialize(fileContent);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

}
