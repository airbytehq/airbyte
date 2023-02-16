/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.google.errorprone.annotations.MustBeClosed;
import com.zaxxer.hikari.pool.HikariProxyResultSet;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.streaming.JdbcStreamingQueryConfig;
import java.lang.reflect.Field;
import java.sql.Blob;
import java.sql.Clob;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLData;
import java.sql.SQLException;
import java.sql.Struct;
import java.util.Map;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import javax.sql.DataSource;
import javax.sql.RowSet;
import javax.sql.RowSetMetaData;
import javax.sql.rowset.CachedRowSet;
import javax.sql.rowset.RowSetMetaDataImpl;
import javax.sql.rowset.RowSetProvider;
import javax.sql.rowset.serial.SerialArray;
import javax.sql.rowset.serial.SerialBlob;
import javax.sql.rowset.serial.SerialClob;
import javax.sql.rowset.serial.SerialStruct;
import org.postgresql.core.Tuple;
import org.postgresql.jdbc.PgResultSet;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This database allows a developer to specify a {@link JdbcStreamingQueryConfig}. This allows the
 * developer to specify the correct configuration in order for a {@link PreparedStatement} to
 * execute as in a streaming / chunked manner.
 */
public class StreamingJdbcDatabase extends DefaultJdbcDatabase {

  private static final Logger LOGGER = LoggerFactory.getLogger(StreamingJdbcDatabase.class);

  private final Supplier<JdbcStreamingQueryConfig> streamingQueryConfigProvider;

  public StreamingJdbcDatabase(final DataSource dataSource,
                               final JdbcCompatibleSourceOperations<?> sourceOperations,
                               final Supplier<JdbcStreamingQueryConfig> streamingQueryConfigProvider) {
    super(dataSource, sourceOperations);
    this.streamingQueryConfigProvider = streamingQueryConfigProvider;
  }

  /**
   * Assuming that the {@link JdbcStreamingQueryConfig} is configured correctly for the JDBC driver
   * being used, this method will return data in streaming / chunked fashion. Review the provided
   * {@link JdbcStreamingQueryConfig} to understand the size of these chunks. If the entire stream is
   * consumed the database connection will be closed automatically and the caller need not call close
   * on the returned stream. This query (and the first chunk) are fetched immediately. Subsequent
   * chunks will not be pulled until the first chunk is consumed.
   *
   * @param statementCreator create a {@link PreparedStatement} from a {@link Connection}.
   * @param recordTransform transform each record of that result set into the desired type. do NOT
   *        just pass the {@link ResultSet} through. it is a stateful object will not be accessible if
   *        returned from recordTransform.
   * @param <T> type that each record will be mapped to.
   * @return Result of the query mapped to a stream. This stream must be closed!
   * @throws SQLException SQL related exceptions.
   */
  @Override
  @MustBeClosed
  public <T> Stream<T> unsafeQuery(final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator,
                                   final CheckedFunction<ResultSet, T, SQLException> recordTransform)
      throws SQLException {
    try {
      final Connection connection = dataSource.getConnection();
      final PreparedStatement statement = statementCreator.apply(connection);
      final JdbcStreamingQueryConfig streamingConfig = streamingQueryConfigProvider.get();
      streamingConfig.initialize(connection, statement);
      return toUnsafeStream(statement.executeQuery(), recordTransform, streamingConfig)
          .onClose(() -> {
            try {
              connection.setAutoCommit(true);
              connection.close();
              if (isStreamFailed) {
                throw new RuntimeException(streamException);
              }
            } catch (final SQLException e) {
              throw new RuntimeException(e);
            }
          });
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  @MustBeClosed
  public Stream<Tuple> unsafeQueryRS(final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator)
      throws SQLException {
    try {
      final Connection connection = dataSource.getConnection();
      final PreparedStatement statement = statementCreator.apply(connection);
      final JdbcStreamingQueryConfig streamingConfig = streamingQueryConfigProvider.get();
      streamingConfig.initialize(connection, statement);
      statement.setFetchSize(100_000);
      return toUnsafeStreamRS(statement.executeQuery(), streamingConfig)
          .onClose(() -> {
            try {
              connection.setAutoCommit(true);
              connection.close();
              if (isStreamFailed) {
                throw new RuntimeException(streamException);
              }
            } catch (final SQLException e) {
              throw new RuntimeException(e);
            }
          });
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * This method differs from {@link DefaultJdbcDatabase#toUnsafeStream} in that it takes a streaming
   * config that adjusts the fetch size dynamically according to sampled row size.
   */
  protected <T> Stream<T> toUnsafeStream(final ResultSet resultSet,
                                         final CheckedFunction<ResultSet, T, SQLException> mapper,
                                         final JdbcStreamingQueryConfig streamingConfig) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {

      @Override
      public boolean tryAdvance(final Consumer<? super T> action) {
        try {
//          LOGGER.info("*** try advance. action: {}", action);
          if (!resultSet.next()) {
            resultSet.close();
            return false;
          }

          final T dataRow = mapper.apply(resultSet);
          streamingConfig.accept(resultSet, dataRow);
          action.accept(dataRow);
          return true;
        } catch (final SQLException e) {
          LOGGER.error("SQLState: {}, Message: {}", e.getSQLState(), e.getMessage());
          streamException = e;
          isStreamFailed = true;
          // throwing an exception in tryAdvance() method lead to the endless loop in Spliterator and stream
          // will never close
          return false;
        }
      }

    }, false);
  }

  protected Stream<Tuple> toUnsafeStreamRS(final ResultSet resultSet,
                                            final JdbcStreamingQueryConfig streamingConfig) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {
      ResultSetMetaData rsmd;
      RowSetMetaData md;
      Field privateField;
      PgResultSet pgrs;
      @Override
      public boolean tryAdvance(final Consumer<? super Tuple> action) {
        try {
//           LOGGER.info("*** try advance");
          if (!resultSet.next()) {
            resultSet.close();
            return false;
          }

//          final CachedRowSet rowSet = RowSetProvider.newFactory().createCachedRowSet();

//          rowSet.setPageSize(1);
//          rowSet.setMaxRows(1);
          // LOGGER.info("*** populate");

          try {
            if (rsmd == null) {
              resultSet.setFetchSize(100_000);
              rsmd = resultSet.getMetaData();
            }

            if (pgrs == null) {
              final HikariProxyResultSet hprs = (HikariProxyResultSet) resultSet;
              pgrs = hprs.unwrap(PgResultSet.class);
            }
            if (privateField == null) {
              privateField = PgResultSet.class.getDeclaredField("thisRow");
              privateField.setAccessible(true);
            }

            if (StreamingJdbcDatabase.this.currentMetaData == null) {
              StreamingJdbcDatabase.this.currentMetaData = rsmd;
            }
/*
            if (md == null) {
              md = new RowSetMetaDataImpl();
              md.setColumnCount(rsmd.getColumnCount());
              for (int col = 1; col <= md.getColumnCount(); col++) {
                md.setAutoIncrement(col, rsmd.isAutoIncrement(col));
                // if(rsmd.isAutoIncrement(col))
                // updateOnInsert = true;
                md.setCaseSensitive(col, rsmd.isCaseSensitive(col));
                md.setCurrency(col, rsmd.isCurrency(col));
                md.setNullable(col, rsmd.isNullable(col));
                md.setSigned(col, rsmd.isSigned(col));
                md.setSearchable(col, rsmd.isSearchable(col));
                int size = rsmd.getColumnDisplaySize(col);
                if (size < 0) {
                  size = 0;
                }
                md.setColumnDisplaySize(col, size);
                md.setColumnLabel(col, rsmd.getColumnLabel(col));
                md.setColumnName(col, rsmd.getColumnName(col));
                md.setSchemaName(col, rsmd.getSchemaName(col));
                int precision = rsmd.getPrecision(col);
                if (precision < 0) {
                  precision = 0;
                }
                md.setPrecision(col, precision);

                */
/*
                 * It seems, from a bug report, that a driver can sometimes return a negative value for scale.
                 * javax.sql.rowset.RowSetMetaDataImpl will throw an exception if we attempt to set a negative
                 * value. As such, we'll check for this case.
                 *//*

                int scale = rsmd.getScale(col);
                if (scale < 0) {
                  scale = 0;
                }
                md.setScale(col, scale);
                md.setTableName(col, rsmd.getTableName(col));
                md.setCatalogName(col, rsmd.getCatalogName(col));
                md.setColumnType(col, rsmd.getColumnType(col));
                md.setColumnTypeName(col, rsmd.getColumnTypeName(col));
              }
            }
            rowSet.setMetaData(md);
            final Map<String, Class<?>> map = rowSet.getTypeMap();
            Object obj;
            rowSet.moveToInsertRow();
            for (int i = 1; i <= md.getColumnCount(); i++) {
              if (map == null || map.isEmpty()) {
                obj = resultSet.getObject(i);
              } else {
                obj = resultSet.getObject(i, map);
              }

              if (obj instanceof Struct) {
                obj = new SerialStruct((Struct) obj, map);
              } else if (obj instanceof SQLData) {
                obj = new SerialStruct((SQLData) obj, map);
              } else if (obj instanceof Blob) {
                obj = new SerialBlob((Blob) obj);
              } else if (obj instanceof Clob) {
                obj = new SerialClob((Clob) obj);
              } else if (obj instanceof java.sql.Array) {
                if (map != null)
                  obj = new SerialArray((java.sql.Array) obj, map);
                else
                  obj = new SerialArray((java.sql.Array) obj);
              }
//              LOGGER.info("*** set rowset {} {}", i, obj);
              rowSet.updateObject(i, obj);
            }
            // LOGGER.info("*** insertRow");
            rowSet.insertRow();
            rowSet.moveToCurrentRow();
            rowSet.beforeFirst();
            rowSet.next();
*/

          } catch (final Exception ex) {
            LOGGER.info("*** populated?", ex);
          }

          // LOGGER.info("*** rowset size: {}", rowSet.size());
          final Tuple row = (Tuple)privateField.get(pgrs);
//          row = row.readOnlyCopy(); // Temp
//          LOGGER.info("*** got {} bytes", row.length());
          action.accept(row);
//          LOGGER.info("*** accepted");
          return true;
        } catch (final SQLException e) {
          LOGGER.error("SQLState: {}, Message: {}", e.getSQLState(), e.getMessage());
          streamException = e;
          isStreamFailed = true;
          // throwing an exception in tryAdvance() method lead to the endless loop in Spliterator and stream
          // will never close
          return false;
        } catch (final IllegalAccessException e) {
          LOGGER.error("Illegal access", e);
          isStreamFailed = true;
          return false;
        }
      }

    }, false);
  }

}
