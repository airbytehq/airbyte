/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake_bulk;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
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
import java.util.List;
import java.util.function.Consumer;
import org.apache.commons.lang3.StringUtils;
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
  private final List<AirbyteRecordMessage> messageList;

  private final SnowflakeSqlGenerator sqlGenerator;
  private final DefaultTyperDeduper typerDeduper;

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
    this.messageList = new ArrayList<>();

    this.sqlGenerator = new SnowflakeSqlGenerator();

    // last so it can use the above
    this.typerDeduper = this.getTyperDeduper();
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

    LOGGER.info("record: {}", recordMessage);

    this.messageList.add(recordMessage);
    if (this.messageList.size() >= MAX_BULK_FILES) {
      // upload now
      this.flush();
    }
  }

  private void flush() {
    if (this.messageList.size() == 0) {
      return;
    }
    LOGGER.info("uploading {} files", this.messageList.size());

    final String tableName = "testing"; // TODO: use sqlGenerator to get right table name
                                        // TODO: actually, have to know the streams! so we need to make a map

    final String sql = getSqlForMessages(tableName, this.configStaging, this.configFormat, this.messageList);
    LOGGER.info("runSql {}", sql);
    this.messageList.clear();
  }

  @Override
  public void close() throws Exception {
    LOGGER.info("sync close");
    this.flush();
    typerDeduper.commitFinalTables();
    typerDeduper.cleanup();
    LOGGER.info("sync complete");
  }

  // from SnowflakeInternalStagingDestination.getSerializedMessageConsumer
  private DefaultTyperDeduper getTyperDeduper() {
    final String defaultNamespace = this.config.get("schema").asText();
    for (final ConfiguredAirbyteStream stream : this.catalog.getStreams()) {
      if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
        stream.getStream().setNamespace(defaultNamespace);
      }
    }

    final JdbcDatabase database = this.database;
    final String databaseName = this.config.get(JdbcUtils.DATABASE_KEY).asText();
    final SnowflakeDestinationHandler snowflakeDestinationHandler = new SnowflakeDestinationHandler(databaseName, database);
    final CatalogParser catalogParser = new CatalogParser(this.sqlGenerator);
    final ParsedCatalog parsedCatalog = catalogParser.parseCatalog(this.catalog);
    // todo: mess with catalog
    final SnowflakeV1V2Migrator migrator = new SnowflakeV1V2Migrator(this.namingResolver, database, databaseName);
    final SnowflakeV2TableMigrator v2TableMigrator = new SnowflakeV2TableMigrator(database, databaseName, this.sqlGenerator, snowflakeDestinationHandler);
    return new DefaultTyperDeduper<>(this.sqlGenerator, snowflakeDestinationHandler, parsedCatalog, migrator, v2TableMigrator, 8);
  }

  private static String getSqlForMessages(
      final String tableName, final String stagingName, final String formatName,
      final List<AirbyteRecordMessage> messages) {
    final StringBuffer sb = new StringBuffer();
    sb.append("COPY INTO ");
    sb.append(tableName); // todo: escape
    sb.append(" FROM @");
    sb.append(stagingName); // todo: escape
    sb.append(" FILE_FORMAT = ");
    sb.append(formatName); // todo: escape
    sb.append(" FILES = (");
    for (int i = 0; i < messages.size(); i++) {
      final String fileName = messages.get(i).getData().get("file_name").asText();
      if (i > 0) {
        sb.append(", ");
      }
      sb.append("'");
      sb.append(fileName);
      sb.append("'");
    }
    sb.append(");");
    return sb.toString();
  }
}
