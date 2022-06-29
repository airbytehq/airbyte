/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.JsonSchemaType;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.jupiter.api.Test;

public class RedshiftS3StagingInsertDestinationAcceptanceTest extends RedshiftStagingS3DestinationAcceptanceTest {

  public static final String DATASET_ID = Strings.addRandomSuffix("airbyte_tests", "_", 8);
  private static final String TYPE = "type";
  private ConfiguredAirbyteCatalog catalog;

  private static final Instant NOW = Instant.now();

  private static final String USERS_STREAM_NAME = "users_" + RandomStringUtils.randomAlphabetic(5);
  private static final String BOOKS_STREAM_NAME = "books_" + RandomStringUtils.randomAlphabetic(5);

  private static final AirbyteMessage MESSAGE_BOOKS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(BOOKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "Harry Potter").put("id", "10").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_BOOKS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(BOOKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "The Great Gatsby").put("id", "30").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage BOOKS_IN_THE_DB = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(BOOKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "Brave New World").put("id", "1").build()))
          .withEmittedAt(NOW.toEpochMilli()));

  private static final AirbyteMessage MESSAGE_STATE = new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.builder().put("checkpoint", "now!").build())));

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config_staging.json")));
  }

  void setup() {
    MESSAGE_BOOKS1.getRecord().setNamespace(DATASET_ID);
    MESSAGE_BOOKS2.getRecord().setNamespace(DATASET_ID);
    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        CatalogHelpers.createConfiguredAirbyteStream(BOOKS_STREAM_NAME, DATASET_ID,
            io.airbyte.protocol.models.Field.of("name", JsonSchemaType.STRING),
            io.airbyte.protocol.models.Field.of("id", JsonSchemaType.STRING))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)));
  }

  @Test
  void testIfSuperTmpTableWasCreatedAfterVarcharTmpTableDuringS3Staging() throws Exception {
    setup();
    final Database database = getDatabase();
    final String booksStream = getNamingResolver().getRawTableName(BOOKS_STREAM_NAME);
    final String usersStream = getNamingResolver().getRawTableName(USERS_STREAM_NAME);
    createTmpTableWithVarchar(database, usersStream);
    createTmpTableWithVarchar(database, booksStream);

    assertTrue(isTmpTableDataColumnInExpectedType(database, DATASET_ID, booksStream, "character varying"));

    final Destination destination = new RedshiftDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);
    consumer.start();
    consumer.accept(MESSAGE_BOOKS1);
    consumer.accept(MESSAGE_BOOKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    assertTrue(isTmpTableDataColumnInExpectedType(database, DATASET_ID, booksStream, "super"));
    assertTrue(isTmpTableDataColumnInExpectedType(database, DATASET_ID, usersStream, "character varying"));

    final List<JsonNode> booksActual = retrieveRecords(testDestinationEnv, BOOKS_STREAM_NAME, DATASET_ID, config);
    final List<JsonNode> expectedUsersJson = Lists.newArrayList(
        MESSAGE_BOOKS1.getRecord().getData(),
        MESSAGE_BOOKS2.getRecord().getData(),
        BOOKS_IN_THE_DB.getRecord().getData());
    assertEquals(expectedUsersJson.size(), booksActual.size());
    assertTrue(expectedUsersJson.containsAll(booksActual) && booksActual.containsAll(expectedUsersJson));
  }

  private void createTmpTableWithVarchar(final Database database, final String streamName) throws SQLException {
    // As we don't care about the previous data we just simulate the flow when previous table exists.
    database.query(q -> {
      q.fetch(String.format("CREATE SCHEMA IF NOT EXISTS %s", DATASET_ID));
      q.fetch(String.format(
          "CREATE TABLE IF NOT EXISTS %s.%s (%s VARCHAR PRIMARY KEY, %s VARCHAR, %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)",
          DATASET_ID,
          streamName,
          JavaBaseConstants.COLUMN_NAME_AB_ID,
          JavaBaseConstants.COLUMN_NAME_DATA,
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT));
      // Simulate existing record
      q.fetch(String.format("""
                            insert into %s.%s (_airbyte_ab_id, _airbyte_data, _airbyte_emitted_at) values
                            ('9', '{\"id\":\"1\",\"name\":\"Brave New World\"}', '2022-02-09 12:02:13.322000 +00:00')""",
          DATASET_ID,
          streamName));
      return null;
    });
  }

  /**
   * @param database - current database properties
   * @param dataSet - current catalog
   * @param streamName - table name
   * @param expectedType - data type of _airbyte_data to expect
   * @return if current datatype of _airbyte_data column is expectedType.
   *
   *         PG_TABLE_DEF table Stores information about table columns. PG_TABLE_DEF only returns
   *         information about tables that are visible to the user.
   *
   *         <a href=
   *         "https://docs.aws.amazon.com/redshift/latest/dg/r_PG_TABLE_DEF.html">PG_TABLE_DEF</a>
   *
   * @throws SQLException
   */
  private boolean isTmpTableDataColumnInExpectedType(final Database database,
                                                     final String dataSet,
                                                     final String streamName,
                                                     final String expectedType)
      throws SQLException {
    Result<Record> query = database.query(q -> {
      return q.fetch(String.format("""
                                   set search_path to %s;
                                   select type from pg_table_def where tablename = \'%s\' and "column" = \'%s\'""",
          dataSet, streamName, JavaBaseConstants.COLUMN_NAME_DATA));
    });
    return query.get(0).getValue(TYPE).toString().trim().contains(expectedType);
  }

}
