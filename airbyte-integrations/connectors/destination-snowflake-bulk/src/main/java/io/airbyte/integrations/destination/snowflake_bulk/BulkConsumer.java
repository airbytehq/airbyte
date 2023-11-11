/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake_bulk;

import static java.util.stream.Collectors.joining;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV2TableMigrator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BulkConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BulkConsumer.class);

  private static final String CONFIG_STAGE_KEY = "snowflake_stage_name";
  private static final String CONFIG_FORMAT_KEY = "snowflake_file_format";
  private static final int MAX_BULK_FILES = 5; // TODO: 1000
                                               // https://docs.snowflake.com/en/sql-reference/sql/copy-into-table#optional-parameters

  private final JsonNode config;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final SqlOperations sqlOperations;
  private final JdbcDatabase database;
  private final ConfiguredAirbyteCatalog catalog;
  private final NamingConventionTransformer namingResolver;

  private final String configStaging;
  private final String configFormat;
  private final Map<StreamConfig, List<AirbyteRecordMessage>> streamMessages;

  private final SnowflakeSqlGenerator sqlGenerator;
  private final String defaultNamespace;
  private DefaultTyperDeduper typerDeduper;
  private ParsedCatalog parsedCatalog;

  public static final String QUOTE = "\"";

  // same as JdbcBufferedConsumerFactory
  public BulkConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
      final JdbcDatabase database,
      final SqlOperations sqlOperations,
      final NamingConventionTransformer namingResolver,
      final JsonNode config,
      final ConfiguredAirbyteCatalog catalog) {

    this.config = config;
    this.outputRecordCollector = outputRecordCollector;
    this.sqlOperations = sqlOperations;
    this.database = database;
    this.catalog = catalog;
    this.namingResolver = namingResolver;

    this.configStaging = config.get(CONFIG_STAGE_KEY).asText();
    this.configFormat = config.get(CONFIG_FORMAT_KEY).asText();
    this.streamMessages = new HashMap<>();

    this.sqlGenerator = new SnowflakeSqlGenerator();

    this.defaultNamespace = this.config.get("schema").asText();
    // set up other instance variables using the above
    this.setTyperDeduperAndCatalog();
  }

  // from SnowflakeInternalStagingDestination.getSerializedMessageConsumer
  private void setTyperDeduperAndCatalog() {
    for (final ConfiguredAirbyteStream stream : this.catalog.getStreams()) {
      if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
        stream.getStream().setNamespace(this.defaultNamespace);
      }
    }

    final CatalogParser catalogParser = new CatalogParser(this.sqlGenerator);
    final ParsedCatalog parsedCatalog = catalogParser.parseCatalog(this.catalog);
    fixupCatalogForBulkTest(parsedCatalog);
    this.parsedCatalog = parsedCatalog;

    final JdbcDatabase database = this.database;
    final String databaseName = this.config.get(JdbcUtils.DATABASE_KEY).asText();
    final SnowflakeDestinationHandler snowflakeDestinationHandler = new SnowflakeDestinationHandler(databaseName, database);

    final SnowflakeV1V2Migrator migrator = new SnowflakeV1V2Migrator(this.namingResolver, database, databaseName);
    final SnowflakeV2TableMigrator v2TableMigrator = new SnowflakeV2TableMigrator(database, databaseName, this.sqlGenerator, snowflakeDestinationHandler);
    final DefaultTyperDeduper typerDeduper = new DefaultTyperDeduper<>(this.sqlGenerator, snowflakeDestinationHandler, parsedCatalog, migrator, v2TableMigrator, 8);
    this.typerDeduper = typerDeduper;

  }

  @Override
  public void start() throws Exception {
    LOGGER.info("start staging:{} format:{}", this.configStaging, this.configFormat);
    typerDeduper.prepareTables();
    LOGGER.info("tables created");
  }

  @Override
  public void accept(final AirbyteMessage message) {
    if (message.getType() == Type.STATE) {
      LOGGER.info("Emitting state: {}", message);
      outputRecordCollector.accept(message);
      return;
    } else if (message.getType() != Type.RECORD) {
      return;
    }

    final AirbyteRecordMessage recordMessage = message.getRecord();
    if (StringUtils.isEmpty(recordMessage.getNamespace())) {
      recordMessage.setNamespace(this.defaultNamespace);
    }

    LOGGER.info("record: {}", recordMessage);
    final String streamName = recordMessage.getStream();
    final String namespace = recordMessage.getNamespace();

    final StreamConfig stream = this.parsedCatalog.getStream(namespace, streamName);

    LOGGER.info("stream: {}", stream);

    if(!this.streamMessages.containsKey(stream)) {
      LOGGER.info("  does not have key: {}", stream);
      this.streamMessages.put(stream, new ArrayList<>()); // TODO: not sure this stream is a reliable hash key
    }
    final List messageList = this.streamMessages.get(stream);
    messageList.add(recordMessage);

    if (messageList.size() >= MAX_BULK_FILES) {
      // upload now
      this.flush(stream, messageList);
    }
  }

  private void flush(final StreamConfig stream, final List messages) {
    if (messages == null || messages.size() == 0) {
      return;
    }
    LOGGER.info("uploading stream:{} count:{}", stream, messages.size());

    final String sql = getSqlForMessages(stream, this.configStaging, this.configFormat, messages);
    LOGGER.info("runSql {}", sql);
    messages.clear();
  }

  @Override
  public void close() throws Exception {
    LOGGER.info("sync close");
    // flush anything left
    for(final Map.Entry<StreamConfig, List<AirbyteRecordMessage>> entry : this.streamMessages.entrySet()) {
      this.flush(entry.getKey(), entry.getValue());
    }

    this.typerDeduper.commitFinalTables();
    this.typerDeduper.cleanup();
    LOGGER.info("sync complete");
  }


  private ColumnId colId(final String name) {
    return this.sqlGenerator.buildColumnId(name, "");
  }
  private void fillKnownSchema(final HashMap<ColumnId, AirbyteType> columns) {
    columns.clear();

    // Example data
    // 3044296966|181148939|3648958|7|33.00|65303.04|0.07|0.01|R|F|1994-11-21|1994-11-02|1994-12-18|COLLECT COD|AIR|tes cajole among the furiously dogg
    // 4652478305|186711564|6711565|1|6.00|9397.38|0.06|0.08|R|F|1995-04-24|1995-02-12|1995-05-09|DELIVER IN PERSON|SHIP| ideas integrate furiou

    columns.put(colId("F1"), AirbyteProtocolType.INTEGER);
    columns.put(colId("F2"), AirbyteProtocolType.INTEGER);
    columns.put(colId("F3"), AirbyteProtocolType.INTEGER);
    columns.put(colId("F4"), AirbyteProtocolType.INTEGER);
    columns.put(colId("F5"), AirbyteProtocolType.NUMBER);
    columns.put(colId("F6"), AirbyteProtocolType.NUMBER);
    columns.put(colId("F7"), AirbyteProtocolType.NUMBER);
    columns.put(colId("F8"), AirbyteProtocolType.NUMBER);
    columns.put(colId("F9"), AirbyteProtocolType.STRING);
    columns.put(colId("F10"), AirbyteProtocolType.STRING);
    columns.put(colId("F11"), AirbyteProtocolType.STRING); // DATE is actually a full DATETIME
    columns.put(colId("F12"), AirbyteProtocolType.STRING); // DATE is actually a full DATETIME
    columns.put(colId("F13"), AirbyteProtocolType.STRING); // DATE is actually a full DATETIME
    columns.put(colId("F14"), AirbyteProtocolType.STRING);
    columns.put(colId("F15"), AirbyteProtocolType.STRING);
    columns.put(colId("F16"), AirbyteProtocolType.STRING);
  }

  private void fixupCatalogForBulkTest(final ParsedCatalog parsedCatalog) {
    for(final StreamConfig stream : parsedCatalog.streams()) {
      fillKnownSchema(stream.columns());
    }

//    for(final StreamConfig stream : parsedCatalog.streams()) {
//      LOGGER.info(" streamname: {}", stream.id().rawName());
//      final HashMap<ColumnId, AirbyteType> columns = stream.columns();
//      for(final Map.Entry<ColumnId, AirbyteType> entry : columns.entrySet()) {
//        final ColumnId columnId = entry.getKey();
//        final AirbyteType type = entry.getValue();
//        LOGGER.info("        column id:{} type:{}", columnId, type);
//      }
//    }
  }

  // Like createTable from SnowflakeSqlGenerator with Airbyte columns removed
  public String createTableTmp(final StreamConfig stream, final String suffix, final boolean force) {
    final String columnDeclarations = stream.columns().entrySet().stream()
        .map(column -> column.getKey().name(QUOTE) + " " + this.sqlGenerator.toDialectType(column.getValue()))
        .collect(joining(",\n"));
    final String forceCreateTable = force ? "OR REPLACE" : "";

    return new StringSubstitutor(Map.of(
        "final_namespace", stream.id().finalNamespace(QUOTE),
        "final_table_id", stream.id().finalTableId(QUOTE, suffix.toUpperCase()),
        "force_create_table", forceCreateTable,
        "column_declarations", columnDeclarations)).replace(
        """
        CREATE SCHEMA IF NOT EXISTS ${final_namespace};

        CREATE ${force_create_table} TABLE ${final_table_id} (
          ${column_declarations}
        );
        """);
  }


  private String getSqlForMessages(
      final StreamConfig stream, final String stagingName, final String formatName,
      final List<AirbyteRecordMessage> messages) {

    final StringBuffer sb = new StringBuffer();

    final String tempSuffix = "_TMP";
    final String tempSql = this.createTableTmp(stream, tempSuffix, true);

    sb.append(tempSql);
    sb.append("\n");

    sb.append("COPY INTO ");
    sb.append(stream.id().finalTableId(QUOTE, tempSuffix));
    sb.append(" FROM '@");
    sb.append(stagingName);
    sb.append("'");
    sb.append(" FILE_FORMAT = ");
    sb.append("'" + formatName + "'");
    sb.append(" FILES = (");
    for (int i = 0; i < messages.size(); i++) {
      final String fileName = messages.get(i).getData().get("file_name").asText();
      if (i > 0) {
        sb.append(",\n");
      }
      sb.append("'");
      sb.append(fileName);
      sb.append("'");
    }
    sb.append(");");

    sb.append("\n");


    // F1, F2, ..., F16
    final String columns = stream.columns().entrySet().stream()
        .map(column -> column.getKey().name(QUOTE))
        .collect(joining(","));

    final String loadAndDropSql = new StringSubstitutor(Map.of(
        "final_table_id", stream.id().finalTableId(QUOTE),
        "temp_table_id", stream.id().finalTableId(QUOTE, tempSuffix),
        "columns", columns)).replace(
        """
        INSERT INTO ${final_table_id} (_AIRBYTE_RAW_ID, _AIRBYTE_EXTRACTED_AT, _AIRBYTE_META, ${columns})
        SELECT UUID_STRING(), CURRENT_TIMESTAMP(), PARSE_JSON('{}'),* FROM ${temp_table_id}
        ;
        
        DROP TABLE ${temp_table_id};
       """);

    sb.append(loadAndDropSql);
    sb.append("\n");

    return sb.toString();
  }


}


// Example full SQL
//  CREATE OR REPLACE TABLE "BULK_TEST"."FILES_TMP" (
//  "F1" NUMBER,
//  "F2" NUMBER,
//  "F3" NUMBER,
//  "F4" NUMBER,
//  "F5" FLOAT,
//  "F6" FLOAT,
//  "F7" FLOAT,
//  "F8" FLOAT,
//  "F9" TEXT,
//  "F10" TEXT,
//  "F11" TEXT,
//  "F12" TEXT,
//  "F13" TEXT,
//  "F14" TEXT,
//  "F15" TEXT,
//  "F16" TEXT
//  );
//
//  COPY INTO "BULK_TEST"."FILES_TMP" FROM '@brian_ext_stage' FILE_FORMAT = 'brian_csv_format' FILES = (
//    'data_0_0_1.csv',
//    'data_0_0_10.csv',
//    'data_0_0_100.csv',
//    'data_0_0_101.csv',
//    'data_0_0_102.csv'
//  );
//  INSERT INTO "BULK_TEST"."FILES" (_AIRBYTE_RAW_ID, _AIRBYTE_EXTRACTED_AT, _AIRBYTE_META, "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15", "F16")
//  SELECT UUID_STRING(), CURRENT_TIMESTAMP(), PARSE_JSON('{}'),* FROM "BULK_TEST"."FILES_TMP"
//  ;
//
//  DROP TABLE "BULK_TEST"."FILES_TMP";

