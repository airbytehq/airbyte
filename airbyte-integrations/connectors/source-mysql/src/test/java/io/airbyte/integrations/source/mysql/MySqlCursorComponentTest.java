package io.airbyte.integrations.source.mysql;

import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;

public class MySqlCursorComponentTest {

  private final MySQLTestDatabase testdb = MySQLTestDatabase.in(MySQLTestDatabase.BaseImage.MYSQL_8);

  @Test
  public void testInitialSync() throws Exception {
    testdb
        .with("CREATE TABLE kv (k INT PRIMARY KEY, v VARCHAR(60), c1 BIT, c2 DATE, c3 DATETIME, c4 TIME, c5 YEAR, c6 BLOB, c7 TIMESTAMP, c8 DECIMAL)")
        .with("INSERT INTO kv (k, v) VALUES (1, 'foo'), (2, 'bar')")
        .with("CREATE TABLE eventlog (ts TIMESTAMP NOT NULL DEFAULT NOW(), msg VARCHAR(60))")
        .with("INSERT INTO eventlog (msg) VALUES ('hello')")
        .with("INSERT INTO eventlog (msg) VALUES ('there')");
    var catalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            "kv",
                testdb.getDatabaseName(),
                Field.of("k", JsonSchemaType.INTEGER),
                Field.of("v", JsonSchemaType.STRING))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withDefaultCursorField(List.of("k"))
            .withSourceDefinedPrimaryKey(List.of(List.of("k"))),
        CatalogHelpers.createAirbyteStream(
                "eventlog",
                testdb.getDatabaseName(),
                Field.of("ts", JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE),
                Field.of("msg", JsonSchemaType.STRING))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withDefaultCursorField(List.of("ts"))
            .withSourceDefinedPrimaryKey(List.of(List.of("ts")))));


    var configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    configuredCatalog.getStreams().forEach(s -> {
      s.setSyncMode(SyncMode.INCREMENTAL);
      s.setDestinationSyncMode(DestinationSyncMode.APPEND);
      s.setCursorField(s.getStream().getDefaultCursorField());
      s.setPrimaryKey(s.getStream().getSourceDefinedPrimaryKey());
    });

    var config = testdb.testConfigBuilder()
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .withoutSsl()
        .build();
    var source = new MySqlSource();
    var discover = source.discover(config);
    var it = source.read(config, configuredCatalog, null);
    final var list = new ArrayList<Object>();
    it.forEachRemaining(list::add);
    list.forEach(System.out::println);
  }


}
