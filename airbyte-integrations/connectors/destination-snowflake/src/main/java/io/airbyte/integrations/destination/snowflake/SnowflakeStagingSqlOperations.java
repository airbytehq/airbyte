package io.airbyte.integrations.destination.snowflake;

import com.google.common.collect.Iterables;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.UUID;

public class SnowflakeStagingSqlOperations extends JdbcSqlOperations implements SqlOperations {

    private static final int MAX_PARTITION_SIZE = 10000;
    private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);

    @Override
    protected void insertRecordsInternal(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String stage) throws Exception {
        if (records.isEmpty()) {
            return;
        }
        for (List<AirbyteRecordMessage> partition : Iterables.partition(records, MAX_PARTITION_SIZE)) {
            try {
                final File tempFile = Files.createTempFile(stage.concat(UUID.randomUUID().toString()), ".csv").toFile();
                loadDataIntoStage(database, partition, stage, tempFile);
                Files.delete(tempFile.toPath());
            } catch (final IOException e) {
                throw new SQLException(e);
            }
        }
    }


    private void loadDataIntoStage(final JdbcDatabase database,
                                   final List<AirbyteRecordMessage> records,
                                   final String stage,
                                   final File tmpFile) throws SQLException {
        database.execute(connection -> {
            try {
                writeBatchToFile(tmpFile, records);
                try (final Statement stmt = connection.createStatement()) {
                    stmt.execute(String.format("PUT file://%s @%s PARALLEL = 4", tmpFile.getAbsolutePath(), stage));
                }
            } catch (final Exception e) {
                throw new RuntimeException(e);
            }
        });
    }

    public void createStageIfNotExists(final JdbcDatabase database, final String stageName) throws SQLException {
        database.execute(String.format("CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE')" +
                " copy_options = (on_error='skip_file');", stageName));
    }

    public void copyIntoTmpTableFromStage(JdbcDatabase database, String stageName, String dstTableName, String schemaName) throws SQLException {
        database.execute(String.format("COPY INTO %s.%s FROM @%s file_format = " +
                        "(type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')",
                schemaName,
                dstTableName,
                stageName));

    }
    public void dropStageIfExists(final JdbcDatabase database, final String stageName) throws SQLException {
        database.execute(String.format("DROP STAGE IF EXISTS %s;", stageName));
    }

    @Override
    public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
        database.execute(createTableQuery(database, schemaName, tableName));
    }

    @Override
    public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
        return String.format(
                "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
                        + "%s VARCHAR PRIMARY KEY,\n"
                        + "%s VARIANT,\n"
                        + "%s TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()\n"
                        + ") data_retention_time_in_days = 0;",
                schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }

}
