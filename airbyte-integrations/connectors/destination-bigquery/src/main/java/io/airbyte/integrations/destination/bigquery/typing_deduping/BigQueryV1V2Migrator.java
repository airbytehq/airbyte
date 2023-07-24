package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationV1V2Migrator;
import io.airbyte.integrations.base.destination.typing_deduping.MigrationResult;
import io.airbyte.integrations.base.destination.typing_deduping.NameAndNamespacePair;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;

import java.util.Collection;
import java.util.Collections;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static io.airbyte.integrations.base.destination.typing_deduping.Constants.RAW_TABLE_EXPECTED_V1_COLUMNS;
import static io.airbyte.integrations.base.destination.typing_deduping.Constants.RAW_TABLE_EXPECTED_V2_COLUMNS;

public class BigQueryV1V2Migrator implements DestinationV1V2Migrator<TableDefinition> {

    private final BigQuery bq;

    public BigQueryV1V2Migrator(final BigQuery bq) {
        this.bq = bq;
    }
    @Override
    public MigrationResult migrate(SqlGenerator<TableDefinition> sqlGenerator, DestinationHandler<TableDefinition> destinationHandler, StreamConfig streamConfig) {
        return null;
    }

    @Override
    public boolean doesAirbyteNamespaceExist(StreamConfig streamConfig) {
        return bq.getDataset(streamConfig.id().rawNamespace()).exists();
    }

    @Override
    public Optional<TableDefinition> getRawTableFromAirbyteSchemaIfExists(StreamConfig streamConfig) {
        Table v2RawTable = bq.getTable(TableId.of(streamConfig.id().rawNamespace(), streamConfig.id().rawName()));
        return v2RawTable.exists() ? Optional.of(v2RawTable.getDefinition()) : Optional.empty();
    }

    @Override
    public Optional<TableDefinition> getV1RawTableIfExists(NameAndNamespacePair v1RawTableNamespacePair) {
        Table v1RawTable = bq.getTable(TableId.of(v1RawTableNamespacePair.namespace(), v1RawTableNamespacePair.tableName()));
        return v1RawTable.exists() ? Optional.of(v1RawTable.getDefinition()) : Optional.empty();
    }

    @Override
    public boolean schemaMatchesExpectation(TableDefinition existingTable, Collection<String> expectedColumnNames) {
        Set<String> existingSchemaColumns = Optional.ofNullable(existingTable.getSchema())
                .map(schema -> schema.getFields().stream()
                        .map(Field::getName)
                        .collect(Collectors.toSet()))
                .orElse(Collections.emptySet());

        return !existingSchemaColumns.isEmpty() &&
                CollectionUtils.containsAllIgnoreCase(expectedColumnNames, existingSchemaColumns);
    }
}
