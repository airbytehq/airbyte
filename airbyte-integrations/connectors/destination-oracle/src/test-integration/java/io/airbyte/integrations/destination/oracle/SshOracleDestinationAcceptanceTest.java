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
import org.jooq.JSONFormat;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

public abstract class SshOracleDestinationAcceptanceTest extends DestinationAcceptanceTest {
    private static final JSONFormat JSON_FORMAT = new JSONFormat().recordFormat(JSONFormat.RecordFormat.OBJECT);

    private final ExtendedNameTransformer namingResolver = new OracleNameTransformer();

    private final String schemaName = "TEST_ORCL_USER";

    public abstract Path getConfigFilePath();

    @Override
    protected String getImageName() {
        return "airbyte/destination-oracle:dev";
    }

    @Override
    protected JsonNode getConfig() {
        final JsonNode config = getConfigFromSecretsFile();
        // do everything in a randomly generated schema so that we can wipe it out at the end.
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
                .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase(Locale.ROOT)).asText()))
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
                                        .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, wrapInQuotes(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)))
                                        .stream()
                                        .map(r -> r.formatJSON(JSON_FORMAT))
                                        .map(Jsons::deserialize)
                                        .collect(Collectors.toList())));
    }

    private static String wrapInQuotes(final String s){
        return '"' + s.toUpperCase(Locale.ROOT) + '"';
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

    @Override
    protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env, final String streamName, final String namespace)
            throws Exception {
        final String tableName = namingResolver.getIdentifier(streamName);
        // Temporarily disabling the behavior of the ExtendedNameTransformer, see (issue #1785) so we don't
        // use quoted names
        // if (!tableName.startsWith("\"")) {
        // // Currently, Normalization always quote tables identifiers
        // //tableName = "\"" + tableName + "\"";
        // }
        return retrieveRecordsFromTable(tableName, namespace);
    }

    @Override
    protected List<String> resolveIdentifier(final String identifier) {
        final List<String> result = new ArrayList<>();
        final String resolved = namingResolver.getIdentifier(identifier);
        result.add(identifier);
        result.add(resolved);
        if (!resolved.startsWith("\"")) {
            result.add(resolved.toLowerCase());
            result.add(resolved.toUpperCase());
        }
        return result;
    }
}
