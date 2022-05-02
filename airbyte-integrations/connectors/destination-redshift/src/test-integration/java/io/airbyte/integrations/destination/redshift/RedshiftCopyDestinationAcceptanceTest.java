/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.Record;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Integration test testing {@link RedshiftCopyS3Destination}. The default Redshift integration test
 * credentials contain S3 credentials - this automatically causes COPY to be selected.
 */
public class RedshiftCopyDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftCopyDestinationAcceptanceTest.class);

  // config from which to create / delete schemas.
  private JsonNode baseConfig;
  // config which refers to the schema that the test is being run in.
  protected JsonNode config;
  private final RedshiftSQLNameTransformer namingResolver = new RedshiftSQLNameTransformer();

  protected TestDestinationEnv testDestinationEnv;

  private final ObjectMapper mapper = new ObjectMapper();

  @Override
  protected String getImageName() {
    return "airbyte/destination-redshift:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new RedshiftTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(j -> j.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
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
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
    if (!tableName.startsWith("\"")) {
      // Currently, Normalization always quote tables identifiers
      tableName = "\"" + tableName + "\"";
    }
    return retrieveRecordsFromTable(tableName, namespace);
  }

  private JsonNode getJsonFromRecord(Record record) {
    ObjectNode node = mapper.createObjectNode();

    Arrays.stream(record.fields()).forEach(field -> {
      var value = record.get(field);

      switch (field.getDataType().getTypeName()) {
        case "varchar", "other":
          var stringValue = (value != null ? value.toString() : null);
          if (stringValue != null && (stringValue.replaceAll("[^\\x00-\\x7F]", "").matches("^\\[.*\\]$")
              || stringValue.replaceAll("[^\\x00-\\x7F]", "").matches("^\\{.*\\}$"))) {
            node.set(field.getName(), Jsons.deserialize(stringValue));
          } else {
            node.put(field.getName(), stringValue);
          }
          break;
        default:
          node.put(field.getName(), (value != null ? value.toString() : null));
      }
    });
    return node;
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    return getDatabase().query(
        ctx -> ctx
            .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            .stream()
            .map(this::getJsonFromRecord)
            .collect(Collectors.toList()));
  }

  // for each test we create a new schema in the database. run the test in there and then remove it.
  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    final String schemaName = Strings.addRandomSuffix("integration_test", "_", 5);
    final String createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName);
    baseConfig = getStaticConfig();
    getDatabase().query(ctx -> ctx.execute(createSchemaQuery));
    final JsonNode configForSchema = Jsons.clone(baseConfig);
    ((ObjectNode) configForSchema).put("schema", schemaName);
    config = configForSchema;
    this.testDestinationEnv = testEnv;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    final String dropSchemaQuery = String.format("DROP SCHEMA IF EXISTS %s CASCADE", config.get("schema").asText());
    getDatabase().query(ctx -> ctx.execute(dropSchemaQuery));
  }

  protected Database getDatabase() {
    return Databases.createDatabase(
        baseConfig.get("username").asText(),
        baseConfig.get("password").asText(),
        String.format("jdbc:redshift://%s:%s/%s",
            baseConfig.get("host").asText(),
            baseConfig.get("port").asText(),
            baseConfig.get("database").asText()),
        "com.amazon.redshift.jdbc.Driver", null,
        RedshiftInsertDestination.SSL_JDBC_PARAMETERS);
  }

  public RedshiftSQLNameTransformer getNamingResolver() {
    return namingResolver;
  }

  @Override
  protected boolean implementsRecordSizeLimitChecks() {
    return true;
  }

  @Override
  protected int getMaxRecordValueLimit() {
    return RedshiftSqlOperations.REDSHIFT_VARCHAR_MAX_BYTE_SIZE;
  }

}
