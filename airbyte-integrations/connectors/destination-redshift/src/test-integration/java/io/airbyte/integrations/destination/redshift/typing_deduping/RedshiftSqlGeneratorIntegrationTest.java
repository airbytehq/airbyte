/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime;
import static io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations.escapeStringLiteral;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.destination.redshift.RedshiftInsertDestination;
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.OffsetTime;
import java.time.ZoneOffset;
import java.util.List;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.conf.Settings;
import org.jooq.impl.DSL;
import org.jooq.impl.DefaultDataType;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class RedshiftSqlGeneratorIntegrationTest extends JdbcSqlGeneratorIntegrationTest<RedshiftState> {

  @Override
  protected boolean getSupportsSafeCast() {
    return true;
  }

  /**
   * Redshift's JDBC driver doesn't map certain data types onto {@link java.sql.JDBCType} usefully.
   * This class adds special handling for those types.
   */
  public static class RedshiftSourceOperations extends JdbcSourceOperations {

    @Override
    public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
      final String columnName = resultSet.getMetaData().getColumnName(colIndex);
      final String columnTypeName = resultSet.getMetaData().getColumnTypeName(colIndex).toLowerCase();

      switch (columnTypeName) {
        // SUPER has no equivalent in JDBCType
        case "super" -> json.set(columnName, Jsons.deserializeExact(resultSet.getString(colIndex)));
        // For some reason, the driver maps these to their timezoneless equivalents (TIME and TIMESTAMP)
        case "timetz" -> putTimeWithTimezone(json, columnName, resultSet, colIndex);
        case "timestamptz" -> putTimestampWithTimezone(json, columnName, resultSet, colIndex);
        default -> super.copyToJsonField(resultSet, colIndex, json);
      }
    }

    @Override
    protected void putTimeWithTimezone(final ObjectNode node,
                                       final String columnName,
                                       final ResultSet resultSet,
                                       final int index)
        throws SQLException {
      final OffsetTime offsetTime = resultSet.getTimestamp(index).toInstant().atOffset(ZoneOffset.UTC).toOffsetTime();
      node.put(columnName, DateTimeConverter.convertToTimeWithTimezone(offsetTime));
    }

    @Override
    protected void putTime(final ObjectNode node,
                           final String columnName,
                           final ResultSet resultSet,
                           final int index)
        throws SQLException {
      putJavaSQLTime(node, columnName, resultSet, index);
    }

    @Override
    protected void putTimestampWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index)
        throws SQLException {
      // The superclass implementation tries to fetch a OffsetDateTime, which fails.
      try {
        super.putTimestampWithTimezone(node, columnName, resultSet, index);
      } catch (final Exception e) {
        final Instant instant = resultSet.getTimestamp(index).toInstant();
        node.put(columnName, DateTimeConverter.convertToTimestampWithTimezone(instant));
      }
    }

    // Base class is converting to Instant which assumes the base timezone is UTC and resolves the local
    // value to system's timezone.
    @Override
    protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
      try {
        node.put(columnName, DateTimeConverter.convertToTimestamp(getObject(resultSet, index, LocalDateTime.class)));
      } catch (final Exception e) {
        final LocalDateTime localDateTime = resultSet.getTimestamp(index).toLocalDateTime();
        node.put(columnName, DateTimeConverter.convertToTimestamp(localDateTime));
      }
    }

  }

  private static DataSource dataSource;
  private static JdbcDatabase database;
  private static String databaseName;

  @BeforeAll
  public static void setupJdbcDatasource() throws Exception {
    final String rawConfig = Files.readString(Path.of("secrets/1s1t_config.json"));
    final JsonNode config = Jsons.deserialize(rawConfig);
    // TODO: Existing in AbstractJdbcDestination, pull out to a util file
    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    // TODO: Its sad to instantiate unneeded dependency to construct database and datsources. pull it to
    // static methods.
    final RedshiftInsertDestination insertDestination = new RedshiftInsertDestination();
    dataSource = insertDestination.getDataSource(config);
    database = insertDestination.getDatabase(dataSource, new RedshiftSourceOperations());
  }

  @AfterAll
  public static void teardownRedshift() throws Exception {
    DataSourceFactory.close(dataSource);
  }

  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return new RedshiftSqlGenerator(new RedshiftSQLNameTransformer()) {

      // Override only for tests to print formatted SQL. The actual implementation should use unformatted
      // to save bytes.
      @Override
      protected DSLContext getDslContext() {
        return DSL.using(getDialect(), new Settings().withRenderFormatted(true));
      }

    };
  }

  @Override
  protected DestinationHandler<RedshiftState> getDestinationHandler() {
    return new RedshiftDestinationHandler(databaseName, database, getNamespace());
  }

  @Override
  protected JdbcDatabase getDatabase() {
    return database;
  }

  @Override
  protected DataType<?> getStructType() {
    return new DefaultDataType<>(null, String.class, "super");
  }

  @Override
  protected SQLDialect getSqlDialect() {
    return SQLDialect.POSTGRES;
  }

  @Override
  protected Field<?> toJsonValue(final String valueAsString) {
    return DSL.function("JSON_PARSE", String.class, DSL.val(escapeStringLiteral(valueAsString)));
  }

  @Override
  @Test
  public void testCreateTableIncremental() throws Exception {
    final Sql sql = getGenerator().createTable(getIncrementalDedupStream(), "", false);
    getDestinationHandler().execute(sql);
    List<DestinationInitialStatus<RedshiftState>> initialStatuses = getDestinationHandler().gatherInitialState(List.of(getIncrementalDedupStream()));
    assertEquals(1, initialStatuses.size());
    final DestinationInitialStatus<RedshiftState> initialStatus = initialStatuses.getFirst();
    assertTrue(initialStatus.isFinalTablePresent());
    assertFalse(initialStatus.isSchemaMismatch());
    // TODO assert on table clustering, etc.
  }

}
