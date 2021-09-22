package io.airbyte.integrations.destination.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.JSONFormat;

import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

public abstract class SshOracleDestinationAcceptanceTest extends DestinationAcceptanceTest {
    private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(JSONFormat.RecordFormat.OBJECT);

    private final ExtendedNameTransformer namingResolver = new OracleNameTransformer();

    private final String schemaName = "TEST_" + RandomStringUtils.randomAlphabetic(6).toUpperCase();

    public abstract Path getConfigFilePath();

    @Override
    protected String getImageName() {
        return "airbyte/destination-oracle:dev";
    }

    @Override
    protected JsonNode getConfig() {
        final JsonNode config = getConfigFromSecretsFile();
        ((ObjectNode) config).put("schema", schemaName);
        return config;
    }

    private JsonNode getConfigFromSecretsFile() {
        return Jsons.deserialize(IOs.readFile(getConfigFilePath()));
    }

    @Override
    protected JsonNode getFailCheckConfig() throws Exception {
        final JsonNode clone = Jsons.clone(getConfig());
        ((ObjectNode) clone).put("password", "wrong password");
        return clone;
    }

    @Override
    protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv, String streamName, String namespace, JsonNode streamSchema) throws Exception {
        List<JsonNode> jsonNodes = retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace);
        return jsonNodes
                .stream()
                .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase()).asText()))
                .collect(Collectors.toList());
    }

    private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws Exception {
        final JsonNode config = getConfig();
        return SshTunnel.sshWrap(
                config,
                OracleDestination.HOST_KEY,
                OracleDestination.PORT_KEY,
                (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
                        .query(
                                ctx -> ctx
                                        .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, OracleDestination.COLUMN_NAME_EMITTED_AT)))
                        .stream()
                        .map(r -> r.formatJSON(JSON_FORMAT))
                        .map(Jsons::deserialize)
                        .collect(Collectors.toList()));
    }

    @Override
    protected void setup(TestDestinationEnv testEnv) throws Exception {
        SshTunnel.sshWrap(
                getConfig(),
                OracleDestination.HOST_KEY,
                OracleDestination.PORT_KEY,
                mangledConfig -> {
                    Database databaseFromConfig = getDatabaseFromConfig(mangledConfig);
                    databaseFromConfig.query(ctx -> ctx.fetch(String.format("CREATE USER %s IDENTIFIED BY %s", schemaName, schemaName)));
                    databaseFromConfig.query(ctx -> ctx.fetch(String.format("GRANT CREATE TABLE TO %s", schemaName)));
                    databaseFromConfig.query(ctx -> ctx.fetch(String.format("ALTER USER %s quota unlimited on USERS", schemaName)));
                });
    }

    private Database getDatabaseFromConfig(final JsonNode config) {
        return Databases.createDatabase(
                config.get("username").asText(),
                config.get("password").asText(),
                String.format("jdbc:oracle:thin:@//%s:%s/%s",
                        config.get("host").asText(),
                        config.get("port").asText(),
                        config.get("sid").asText()),
                "oracle.jdbc.driver.OracleDriver",
                null);
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) throws Exception {
        SshTunnel.sshWrap(
                getConfig(),
                OracleDestination.HOST_KEY,
                OracleDestination.PORT_KEY,
                mangledConfig -> {
                    getDatabaseFromConfig(mangledConfig).query(ctx -> ctx.fetch(String.format("DROP USER %s CASCADE", schemaName)));
                });
    }

    @Override
    protected boolean supportsDBT() {
        return true;
    }

    @Override
    protected boolean implementsNamespaces() {
        return true;
    }
}
