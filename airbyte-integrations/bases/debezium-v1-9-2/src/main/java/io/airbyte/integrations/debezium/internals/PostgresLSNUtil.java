package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.debezium.config.Configuration;
import io.debezium.connector.common.OffsetReader;
import io.debezium.connector.postgresql.PostgresConnectorConfig;
import io.debezium.connector.postgresql.PostgresOffsetContext;
import io.debezium.connector.postgresql.PostgresOffsetContext.Loader;
import io.debezium.connector.postgresql.PostgresPartition;
import io.debezium.connector.postgresql.connection.Lsn;
import io.debezium.pipeline.spi.Offsets;
import io.debezium.pipeline.spi.Partition;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Properties;
import java.util.Set;
import org.apache.kafka.connect.json.JsonConverter;
import org.apache.kafka.connect.runtime.WorkerConfig;
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig;
import org.apache.kafka.connect.storage.FileOffsetBackingStore;
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresLSNUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresLSNUtil.class);

  private final JdbcDatabase database;
  private final JsonNode config;


  public PostgresLSNUtil(JdbcDatabase database, JsonNode config) {
    this.database = database;
    this.config = config;
  }

  public boolean isSavedOffsetAfterReplicationSlotLSN(final Properties properties,
      final ConfiguredAirbyteCatalog catalog,
      final AirbyteFileOffsetBackingStore offsetManager,
      final CheckedFunction<ResultSet, JsonNode, SQLException> recordTransform) {
    try {
      final DebeziumPropertiesManager debeziumPropertiesManager = new DebeziumPropertiesManager(properties, config, catalog, offsetManager,
          Optional.empty());
      final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
      final OptionalLong savedOffset = findSavedOffset(debeziumProperties);

      if (savedOffset.isPresent()) {
        JsonNode replicationSlot = getReplicationSlot(recordTransform);
        if (replicationSlot.has("confirmed_flush_lsn")) {
          final long confirmedFlushLsnOnServerSide = Lsn.valueOf(replicationSlot.get("confirmed_flush_lsn").asText()).asLong();
          LOGGER.info("Replication slot confirmed_flush_lsn : " + confirmedFlushLsnOnServerSide + " Saved offset LSN : " + savedOffset.getAsLong());
          return savedOffset.getAsLong() >= confirmedFlushLsnOnServerSide;
        } else if (replicationSlot.has("restart_lsn")) {
          final long restartLsn = Lsn.valueOf(replicationSlot.get("restart_lsn").asText()).asLong();
          LOGGER.info("Replication slot restart_lsn : " + restartLsn + " Saved offset LSN : " + savedOffset.getAsLong());
          return savedOffset.getAsLong() >= restartLsn;
        }
      }

      return true;

    } catch (SQLException e) {
      throw new RuntimeException(e);
    }

  }

  public OptionalLong findSavedOffset(Properties properties) {

    FileOffsetBackingStore fileOffsetBackingStore = null;
    OffsetStorageReaderImpl engine = null;
    try {
      fileOffsetBackingStore = new FileOffsetBackingStore();
      final Map<String, String> from = Configuration.from(properties).asMap();
      from.put(WorkerConfig.KEY_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
      from.put(WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
      fileOffsetBackingStore.configure(new StandaloneConfig(from));
      fileOffsetBackingStore.start();

      final JsonConverter keyConverter = new JsonConverter();
      keyConverter.configure(Configuration.from(properties).subset("internal.key.converter" + ".", true).asMap(), true);
      final JsonConverter valueConverter = new JsonConverter();
      // Make sure that the JSON converter is configured to NOT enable schemas ...
      final Configuration valueConverterConfig = Configuration.from(properties).edit().with("internal.value.converter" + ".schemas.enable", false)
          .build();
      valueConverter.configure(valueConverterConfig.subset("internal.value.converter" + ".", true).asMap(), false);

      engine = new OffsetStorageReaderImpl(fileOffsetBackingStore, properties.getProperty("name"), keyConverter,
          valueConverter);
      final PostgresConnectorConfig postgresConnectorConfig = new PostgresConnectorConfig(Configuration.from(properties));
      final PostgresCustomLoader loader = new PostgresCustomLoader(postgresConnectorConfig);
      final OffsetReader<Partition, PostgresOffsetContext, Loader> offsetReader = new OffsetReader<>(engine, loader);
      final Set<Partition> partitions = Collections.singleton(new PostgresPartition(postgresConnectorConfig.getLogicalName()));
      final Map<Partition, PostgresOffsetContext> offsets = offsetReader.offsets(partitions);

      return extractLsn(partitions, offsets, loader);

    } finally {
      LOGGER.info("Closing engine and fileOffsetBackingStore");
      if (engine != null) {
        engine.close();
      }

      if (fileOffsetBackingStore != null) {
        fileOffsetBackingStore.stop();
      }
    }
  }

  private OptionalLong extractLsn(final Set<Partition> partitions, final Map<Partition, PostgresOffsetContext> offsets,
      PostgresCustomLoader loader) {
    boolean found = false;
    for (Partition partition : partitions) {
      final PostgresOffsetContext postgresOffsetContext = offsets.get(partition);

      if (postgresOffsetContext != null) {
        found = true;
        LOGGER.info("Found previous partition offset {}: {}", partition, postgresOffsetContext.getOffset());
      }
    }

    if (!found) {
      LOGGER.info("No previous offsets found");
      return OptionalLong.empty();
    }

    final Offsets<Partition, PostgresOffsetContext> of = Offsets.of(offsets);
    final PostgresOffsetContext previousOffset = of.getTheOnlyOffset();

    final Map<String, ?> offset = previousOffset.getOffset();

    if (offset.containsKey("lsn_commit")) {
      return OptionalLong.of((long) offset.get("lsn_commit"));
    } else if (offset.containsKey("lsn")) {
      return OptionalLong.of((long) offset.get("lsn"));
    } else if (loader.getRawOffset().containsKey("lsn")) {
      return OptionalLong.of (Long.parseLong(loader.getRawOffset().get("lsn").toString()));
    }

    return OptionalLong.empty();

  }

  private JsonNode getReplicationSlot(final CheckedFunction<ResultSet, JsonNode, SQLException> recordTransform) throws SQLException {
    final List<JsonNode> matchingSlots = database.queryJsons(connection -> {
      final String sql = "SELECT * FROM pg_replication_slots WHERE slot_name = ? AND plugin = ? AND database = ?";
      final PreparedStatement ps = connection.prepareStatement(sql);
      ps.setString(1, config.get("replication_method").get("replication_slot").asText());
      ps.setString(2, config.get("replication_method").has("plugin") ? config.get("replication_method").get("plugin").asText() : "pgoutput");
      ps.setString(3, config.get(JdbcUtils.DATABASE_KEY).asText());

      LOGGER.info("Attempting to find the named replication slot using the query: {}", ps);

      return ps;
    }, recordTransform);

    return matchingSlots.get(0);
  }

}
