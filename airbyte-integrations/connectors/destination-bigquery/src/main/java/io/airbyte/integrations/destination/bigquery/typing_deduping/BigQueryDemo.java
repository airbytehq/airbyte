package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.TableDefinition;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.ParsedCatalog;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.Optional;

public class BigQueryDemo {

  public static void exampleIncremental() throws Exception {
    BigQuery bq = BigQueryOptions.newBuilder()
        .setProjectId("dataline-integration-testing")
        .build()
        .getService();

    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withStream(new AirbyteStream()
                .withName("users")
                .withNamespace("public")
                .withJsonSchema(Jsons.deserialize("""
                    {
                      "type": "object",
                      "properties": {
                        "id": {"type": "integer"},
                        "updated_at": {"type": "timestamp_with_timezone"},
                        "name": {"type": "string"}
                      }
                    }
                    """)))
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id")))
            .withCursorField(List.of("updated_at"))
    ));

    BigQuerySqlGenerator sqlGenerator = new BigQuerySqlGenerator();
    BigQueryDestinationInteractorThing interactorThing = new BigQueryDestinationInteractorThing(bq);
    CatalogParser<StandardSQLTypeName> catalogParser = new CatalogParser<>(sqlGenerator);

    ParsedCatalog<StandardSQLTypeName> parsedCatalog = catalogParser.parseCatalog(catalog);

    // For each stream, set up its final table
    // We depend on existing destination-bigquery code to set up the raw table
    for (StreamConfig<StandardSQLTypeName> stream : parsedCatalog.streams()) {
      Optional<TableDefinition> tableDefinition = interactorThing.findExistingTable(stream.id());
      String setup;
      if (tableDefinition.isEmpty()) {
        setup = sqlGenerator.createTable(stream);
      } else {
        setup = sqlGenerator.alterTable(stream, tableDefinition.get());
      }
      interactorThing.execute(setup);
    }

    // for each batch:
    // insert raw records (again, this is existing dest-bq code)
    // Each batch belongs to a specific stream, so the async code needs to track the StreamConfig
    StreamConfig<StandardSQLTypeName> currentStream = parsedCatalog.streams().get(0);
    // in reality, this suffix is probably ranzomized/incremented per record batch
    String tmpRawSuffix = "foo";
    String update = sqlGenerator.updateTable(tmpRawSuffix, currentStream);
    interactorThing.execute(update);

    // At the end of the sync:
    for (StreamConfig<StandardSQLTypeName> stream : parsedCatalog.streams()) {
      String deleteOldRawRecords = sqlGenerator.deleteOldRawRecords(stream);
      interactorThing.execute(deleteOldRawRecords);
    }
  }

  public static void exampleFullRefresh() throws Exception {
    BigQuery bq = BigQueryOptions.newBuilder()
        .setProjectId("dataline-integration-testing")
        .build()
        .getService();

    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withStream(new AirbyteStream()
                .withName("users")
                .withNamespace("public")
                .withJsonSchema(Jsons.deserialize("""
                    {
                      "type": "object",
                      "properties": {
                        "id": {"type": "integer"},
                        "updated_at": {"type": "timestamp_with_timezone"},
                        "name": {"type": "string"}
                      }
                    }
                    """)))
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
    ));

    BigQuerySqlGenerator sqlGenerator = new BigQuerySqlGenerator();
    BigQueryDestinationInteractorThing interactorThing = new BigQueryDestinationInteractorThing(bq);
    CatalogParser<StandardSQLTypeName> catalogParser = new CatalogParser<>(sqlGenerator);

    ParsedCatalog<StandardSQLTypeName> parsedCatalog = catalogParser.parseCatalog(catalog);

    // At the start of the sync:
    // We depend on existing destination-bigquery code to set up the raw table
    // And then set up the final table for each stream
    for (StreamConfig<StandardSQLTypeName> stream : parsedCatalog.streams()) {
      Optional<TableDefinition> tableDefinition = interactorThing.findExistingTable(stream.id());
      String setup;
      if (tableDefinition.isEmpty()) {
        setup = sqlGenerator.createTable(stream);
      } else {
        setup = sqlGenerator.alterTable(stream, tableDefinition.get());
      }
      interactorThing.execute(setup);
    }

    // for each batch:
    // insert raw records (again, this is existing dest-bq code, plus new stuff to create a tmp table for each batch)
    StreamConfig<StandardSQLTypeName> currentStream = parsedCatalog.streams().get(0);
    // Note that we also pass a temp suffix for the final table
    String update = sqlGenerator.updateTable("tmp", currentStream);
    interactorThing.execute(update);

    // At the end of the sync:
    for (StreamConfig<StandardSQLTypeName> stream : parsedCatalog.streams()) {
      String overwriteFinalTable = sqlGenerator.overwriteFinalTable("tmp", stream);
      interactorThing.execute(overwriteFinalTable);
    }
    // These queries are noops...
    for (StreamConfig<StandardSQLTypeName> stream : parsedCatalog.streams()) {
      String deleteOldRawRecords = sqlGenerator.deleteOldRawRecords(stream);
      interactorThing.execute(deleteOldRawRecords);
    }
  }

}
