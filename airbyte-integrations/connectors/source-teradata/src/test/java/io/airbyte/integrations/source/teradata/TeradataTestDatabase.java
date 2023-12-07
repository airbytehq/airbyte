package io.airbyte.integrations.source.teradata;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.NonContainer;
import io.airbyte.cdk.testutils.TestDatabase;
import org.jooq.SQLDialect;

import java.util.stream.Stream;

public class TeradataTestDatabase extends TestDatabase<NonContainer, TeradataTestDatabase, TeradataTestDatabase.TeradataDbConfigBuilder> {
    private final String username;
    private final String password;
    private final String jdbcUrl;
    private final String databaseName;

    protected TeradataTestDatabase(final JsonNode teradataConfig) {
        super(new NonContainer(teradataConfig.get(JdbcUtils.USERNAME_KEY).asText(),
                teradataConfig.has(JdbcUtils.PASSWORD_KEY) ? teradataConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
                teradataConfig.get(JdbcUtils.JDBC_URL_KEY).asText(), ""));
        this.username = teradataConfig.get(JdbcUtils.USERNAME_KEY).asText();
        this.password = teradataConfig.has(JdbcUtils.PASSWORD_KEY) ? teradataConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null;
        this.jdbcUrl = teradataConfig.get(JdbcUtils.JDBC_URL_KEY).asText();
        this.databaseName = teradataConfig.get(JdbcUtils.SCHEMA_KEY).asText();
    }

    @Override
    public String getDatabaseName() {
        return databaseName;
    }

    @Override
    public String getJdbcUrl() {
        return jdbcUrl;
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public String getUserName() {
        return username;
    }

    @Override
    protected Stream<Stream<String>> inContainerBootstrapCmd() {
        return Stream.empty();
    }

    @Override
    protected Stream<String> inContainerUndoBootstrapCmd() {
        return Stream.empty();
    }

    @Override
    public DatabaseDriver getDatabaseDriver() {
        return DatabaseDriver.TERADATA;
    }

    @Override
    public SQLDialect getSqlDialect() {
        return SQLDialect.DEFAULT;
    }

    @Override
    public void close() {
    }

    static public class TeradataDbConfigBuilder extends TestDatabase.ConfigBuilder<TeradataTestDatabase, TeradataTestDatabase.TeradataDbConfigBuilder> {

        protected TeradataDbConfigBuilder(final TeradataTestDatabase testdb) {
            super(testdb);
        }

    }
}
