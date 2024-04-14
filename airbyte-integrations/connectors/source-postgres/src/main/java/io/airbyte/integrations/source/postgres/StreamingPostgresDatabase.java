package io.airbyte.integrations.source.postgres;

import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.cdk.db.jdbc.streaming.JdbcStreamingQueryConfig;
import org.postgresql.copy.CopyManager;
import org.postgresql.core.BaseConnection;
import org.postgresql.jdbc.PgConnection;

import javax.sql.DataSource;
import java.io.IOException;
import java.io.OutputStream;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.function.Supplier;

public class StreamingPostgresDatabase extends StreamingJdbcDatabase {
    public StreamingPostgresDatabase(final DataSource dataSource, JdbcCompatibleSourceOperations sourceOperations, Supplier<JdbcStreamingQueryConfig> streamingQueryConfigSupplier) {
        super(dataSource, sourceOperations, streamingQueryConfigSupplier);
    }

    @Override
    public void bulkCopyOut(final String sql, final OutputStream outputStream) throws SQLException, IOException {
        final Connection connection = getDataSource().getConnection();
        final BaseConnection baseConnection = connection.unwrap(PgConnection.class);
        final CopyManager copyManager = new CopyManager(baseConnection);
        copyManager.copyOut(sql, outputStream);
        connection.close();
    }
}
