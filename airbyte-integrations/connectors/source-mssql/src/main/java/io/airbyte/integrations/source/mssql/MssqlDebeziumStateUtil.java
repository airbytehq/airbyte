package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.cdk.integrations.debezium.internals.mysql.MysqlCdcStateConstants;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.connector.sqlserver.Lsn;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class MssqlDebeziumStateUtil {
  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlDebeziumStateUtil.class);

  public JsonNode constructInitialDebeziumState(
      final JdbcDatabase database) {
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(
        constructLsnSnapshotState(database, database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText()),
        Optional.empty());
    final Map<String, Object> state = new HashMap<>();
    state.put(MssqlSource.MSSQL_CDC_OFFSET, offsetManager.read());
    return Jsons.jsonNode(state);
  }

  public static MssqlDebeziumStateAttributes getStateAttributesFromDB(final JdbcDatabase database) {
  try (final Stream<MssqlDebeziumStateAttributes> stream = database.unsafeResultSetQuery(
      connection -> connection.createStatement().executeQuery("select sys.fn_cdc_get_max_lsn()"),
      resultSet -> {
        final byte[] lsnBinary = resultSet.getBytes(1);
        Lsn lsn = Lsn.valueOf(lsnBinary);
        return new MssqlDebeziumStateAttributes(lsn);
      })) {
    final List<MssqlDebeziumStateAttributes> stateAttributes = stream.toList();
    assert stateAttributes.size() == 1;
    return stateAttributes.get(0);
  } catch (final SQLException e) {
    throw new RuntimeException(e);
  }
}

public static record MssqlDebeziumStateAttributes(Lsn lsn) {}


  /**
   * Method to construct initial Debezium state which can be passed onto Debezium engine to make it
   * process binlogs from a specific file and position and skip snapshot phase
   * Example:
   * ["test",{"server":"test","database":"test"}]" : "{"transaction_id":null,"event_serial_no":1,"commit_lsn":"00000644:00002ff8:0099","change_lsn":"0000062d:00017ff0:016d"}"
   */
  private JsonNode constructLsnSnapshotState(final JdbcDatabase database, final String dbName) {
    return format(getStateAttributesFromDB(database), dbName, Instant.now());
  }

  @VisibleForTesting
  public JsonNode format(final MssqlDebeziumStateAttributes attributes, final String dbName, final Instant time) {
    final String key = "[\"" + dbName + "\",{\"server\":\"" + dbName + "\"}]";
    final String value =
        "{\"transaction_id\":null,\"event_serial_no\":1,\"commit_lsn\":\"" + attributes.lsn.toString() + "\",\"change_lsn\":"
            + attributes.lsn.toString()
            + ", \"snapshot\":true,\"snapshot_completed\":true"
            + "}";

    final Map<String, String> result = new HashMap<>();
    result.put(key, value);

    final JsonNode jsonNode = Jsons.jsonNode(result);
    LOGGER.info("Initial Debezium state offset constructed: {}", jsonNode);

    return jsonNode;
  }
}