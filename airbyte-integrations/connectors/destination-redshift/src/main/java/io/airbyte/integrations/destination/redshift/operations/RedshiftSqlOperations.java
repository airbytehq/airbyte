/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.operations;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.table;
import static org.jooq.impl.DSL.using;
import static org.jooq.impl.DSL.val;

import com.google.common.collect.Iterables;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;
import org.jooq.DSLContext;
import org.jooq.InsertValuesStep4;
import org.jooq.Record;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSqlOperations extends JdbcSqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSqlOperations.class);
  public static final int REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535;
  public static final int REDSHIFT_SUPER_MAX_BYTE_SIZE = 1000000;

  public RedshiftSqlOperations() {}

  private DSLContext getDslContext() {
    return using(SQLDialect.POSTGRES);
  }

  @Override
  protected String createTableQueryV1(final String schemaName, final String tableName) {
    return String.format("""
                         CREATE TABLE IF NOT EXISTS %s.%s (
                          %s VARCHAR PRIMARY KEY,
                          %s SUPER,
                          %s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)
                          """, schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @Override
  protected String createTableQueryV2(final String schemaName, final String tableName) {
    final DSLContext dsl = getDslContext();
    return dsl.createTableIfNotExists(name(schemaName, tableName))
        .column(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36).nullable(false))
        .column(COLUMN_NAME_AB_EXTRACTED_AT,
            SQLDataType.TIMESTAMPWITHTIMEZONE.defaultValue(function("GETDATE", SQLDataType.TIMESTAMPWITHTIMEZONE)))
        .column(COLUMN_NAME_AB_LOADED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE)
        .column(COLUMN_NAME_DATA, new DefaultDataType<>(null, String.class, "super").nullable(false))
        .getSQL();
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<PartialAirbyteMessage> records,
                                    final String schemaName,
                                    final String tmpTableName)
      throws SQLException {
    LOGGER.info("actual size of batch: {}", records.size());

    // query syntax:
    // INSERT INTO public.users (ab_id, data, emitted_at) VALUES
    // (?, ?::jsonb, ?),
    // ...
    final String insertQueryComponent = String.format(
        "INSERT INTO %s.%s (%s, %s, %s) VALUES\n",
        schemaName,
        tmpTableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    final String recordQueryComponent = "(?, JSON_PARSE(?), ?),\n";
    SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, database, records);
  }

  @Override
  protected void insertRecordsInternalV2(final JdbcDatabase database,
                                         final List<PartialAirbyteMessage> records,
                                         final String schemaName,
                                         final String tableName) {
    try {
      database.execute(connection -> {
        LOGGER.info("Total records received to insert: {}", records.size());
        // This comment was copied from DV1 code (SqlOperationsUtils.insertRawRecordsInSingleQuery):
        // > We also partition the query to run on 10k records at a time, since some DBs set a max limit on
        // > how many records can be inserted at once
        // > TODO(sherif) this should use a smarter, destination-aware partitioning scheme instead of 10k by
        // > default
        for (final List<PartialAirbyteMessage> batch : Iterables.partition(records, 10_000)) {
          LOGGER.info("Prepared batch size: {}, {}, {}", batch.size(), schemaName, tableName);
          final DSLContext create = using(connection, SQLDialect.POSTGRES);
          // JOOQ adds some overhead here. Building the InsertValuesStep object takes about 139ms for 5K
          // records.
          // That's a nontrivial execution speed loss when the actual statement execution takes 500ms.
          // Hopefully we're executing these statements infrequently enough in a sync that it doesn't matter.
          // But this is a potential optimization if we need to eke out a little more performance on standard
          // inserts.
          // ... which presumably we won't, because standard inserts is so inherently slow.
          // See
          // https://github.com/airbytehq/airbyte/blob/f73827eb43f62ee30093451c434ad5815053f32d/airbyte-integrations/connectors/destination-redshift/src/main/java/io/airbyte/integrations/destination/redshift/operations/RedshiftSqlOperations.java#L39
          // and
          // https://github.com/airbytehq/airbyte/blob/f73827eb43f62ee30093451c434ad5815053f32d/airbyte-cdk/java/airbyte-cdk/db-destinations/src/main/java/io/airbyte/cdk/integrations/destination/jdbc/SqlOperationsUtils.java#L62
          // for how DV1 did this in pure JDBC.
          InsertValuesStep4<Record, String, String, OffsetDateTime, OffsetDateTime> insert = create
              .insertInto(table(name(schemaName, tableName)),
                  field(COLUMN_NAME_AB_RAW_ID, SQLDataType.VARCHAR(36)),
                  field(COLUMN_NAME_DATA, new DefaultDataType<>(null, String.class, "super")),
                  field(COLUMN_NAME_AB_EXTRACTED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE),
                  field(COLUMN_NAME_AB_LOADED_AT, SQLDataType.TIMESTAMPWITHTIMEZONE));
          for (final PartialAirbyteMessage record : batch) {
            insert = insert.values(
                val(UUID.randomUUID().toString()),
                function("JSON_PARSE", String.class, val(record.getSerialized())),
                val(Instant.ofEpochMilli(record.getRecord().getEmittedAt()).atOffset(ZoneOffset.UTC)),
                val((OffsetDateTime) null));
          }
          insert.execute();
          LOGGER.info("Executed batch size: {}, {}, {}", batch.size(), schemaName, tableName);
        }
      });
    } catch (final Exception e) {
      LOGGER.error("Error while inserting records", e);
      throw new RuntimeException(e);
    }
  }

}
