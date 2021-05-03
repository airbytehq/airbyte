package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumer;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopier;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class SnowflakeCopyGcsDestination extends CopyDestination {
    @Override
    public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
        return new CopyConsumer<>(
                getConfiguredSchema(config),
                GcsConfig.getGcsConfig(config),
                catalog,
                getDatabase(config),
                new SnowflakeGcsStreamCopierFactory(),
                getSqlOperations(),
                getNameTransformer());
    }

    @Override
    public void checkPersistence(JsonNode config) throws Exception {
        GcsStreamCopier.attemptWriteToPersistence(GcsConfig.getGcsConfig(config));
    }

    @Override
    public ExtendedNameTransformer getNameTransformer() {
        return new SnowflakeSQLNameTransformer();
    }

    @Override
    public JdbcDatabase getDatabase(JsonNode config) throws Exception {
        return SnowflakeDatabase.getDatabase(config);
    }

    @Override
    public SqlOperations getSqlOperations() {
        return new SnowflakeSqlOperations();
    }

    private String getConfiguredSchema(JsonNode config) {
        return config.get("schema").asText();
    }
}
