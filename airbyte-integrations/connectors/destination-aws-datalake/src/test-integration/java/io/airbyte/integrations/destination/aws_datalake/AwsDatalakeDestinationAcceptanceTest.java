/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.aws_datalake;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.athena.model.ColumnInfo;
import software.amazon.awssdk.services.athena.model.Datum;
import software.amazon.awssdk.services.athena.model.GetQueryResultsResponse;
import software.amazon.awssdk.services.athena.model.Row;
import software.amazon.awssdk.services.athena.paginators.GetQueryResultsIterable;

public class AwsDatalakeDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final String CONFIG_PATH = "secrets/config.json";
  private static final Logger LOGGER = LoggerFactory.getLogger(AwsDatalakeDestinationAcceptanceTest.class);

  private JsonNode configJson;
  private JsonNode configInvalidCredentialsJson;
  protected AwsDatalakeDestinationConfig config;
  private AthenaHelper athenaHelper;
  private GlueHelper glueHelper;

  @Override
  protected String getImageName() {
    return "airbyte/destination-aws-datalake:dev";
  }

  @Override
  protected JsonNode getConfig() {
    // TODO: Generate the configuration JSON file to be used for running the destination during the test
    // configJson can either be static and read from secrets/config.json directly
    // or created in the setup method
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    JsonNode credentials = Jsons.jsonNode(ImmutableMap.builder()
        .put("credentials_title", "IAM User")
        .put("aws_access_key_id", "wrong-access-key")
        .put("aws_secret_access_key", "wrong-secret")
        .build());

    JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put("aws_account_id", "112233")
        .put("region", "us-east-1")
        .put("bucket_name", "test-bucket")
        .put("bucket_prefix", "test")
        .put("lakeformation_database_name", "lf_db")
        .put("credentials", credentials)
        .build());

    return config;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws IOException, InterruptedException {
    String query = String.format("SELECT * FROM \"%s\".\"%s\"", config.getDatabaseName(), streamName);
    GetQueryResultsIterable results = athenaHelper.runQuery(config.getDatabaseName(), query);
    return parseResults(results);
  }

  protected List<JsonNode> parseResults(GetQueryResultsIterable queryResults) {

    List<JsonNode> processedResults = new ArrayList<>();

    for (GetQueryResultsResponse result : queryResults) {
      List<ColumnInfo> columnInfoList = result.resultSet().resultSetMetadata().columnInfo();
      Iterator<Row> results = result.resultSet().rows().iterator();
      Row colNamesRow = results.next();
      while (results.hasNext()) {
        Map<String, Object> jsonMap = Maps.newHashMap();
        Row r = results.next();
        Iterator<ColumnInfo> colInfoIterator = columnInfoList.iterator();
        Iterator<Datum> datum = r.data().iterator();
        while (colInfoIterator.hasNext() && datum.hasNext()) {
          ColumnInfo colInfo = colInfoIterator.next();
          Datum value = datum.next();
          Object typedFieldValue = getTypedFieldValue(colInfo, value);
          if (typedFieldValue != null) {
            jsonMap.put(colInfo.name(), typedFieldValue);
          }
        }
        processedResults.add(Jsons.jsonNode(jsonMap));
      }
    }
    return processedResults;
  }

  private static Object getTypedFieldValue(ColumnInfo colInfo, Datum value) {
    var typeName = colInfo.type();
    var varCharValue = value.varCharValue();

    if (varCharValue == null)
      return null;
    var returnType = switch (typeName) {
      case "real", "double", "float" -> Double.parseDouble(varCharValue);
      case "varchar" -> varCharValue;
      case "boolean" -> Boolean.parseBoolean(varCharValue);
      case "integer" -> Integer.parseInt(varCharValue);
      case "row" -> varCharValue;
      default -> null;
    };
    if (returnType == null) {
      LOGGER.warn(String.format("Unsupported type = %s", typeName));
    }
    return returnType;
  }

  @Override
  protected List<String> resolveIdentifier(String identifier) {
    final List<String> result = new ArrayList<>();
    result.add(identifier);
    result.add(identifier.toLowerCase());
    return result;
  }

  private JsonNode loadJsonFile(String fileName) throws IOException {
    final JsonNode configFromSecrets = Jsons.deserialize(IOs.readFile(Path.of(fileName)));
    return (configFromSecrets);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws IOException {
    configJson = loadJsonFile(CONFIG_PATH);

    this.config = AwsDatalakeDestinationConfig.getAwsDatalakeDestinationConfig(configJson);

    Region region = Region.of(config.getRegion());

    AwsBasicCredentials awsCreds = AwsBasicCredentials.create(config.getAccessKeyId(), config.getSecretAccessKey());
    athenaHelper = new AthenaHelper(awsCreds, region, String.format("s3://%s/airbyte_athena/", config.getBucketName()),
        "AmazonAthenaLakeFormation");
    glueHelper = new GlueHelper(awsCreds, region);
    glueHelper.purgeDatabase(config.getDatabaseName());
  }

  private String toAthenaObject(JsonNode value) {
    StringBuilder sb = new StringBuilder("\"{");
    List<String> elements = new ArrayList<>();
    var it = value.fields();
    while (it.hasNext()) {
      Map.Entry<String, JsonNode> f = it.next();
      final String k = f.getKey();
      final String v = f.getValue().asText();
      elements.add(String.format("%s=%s", k, v));
    }
    sb.append(String.join(",", elements));
    sb.append("}\"");
    return sb.toString();
  }

  protected void assertSameValue(final String key, final JsonNode expectedValue, final JsonNode actualValue) {
    if (expectedValue.isObject()) {
      assertEquals(toAthenaObject(expectedValue), actualValue.toString());
    } else {
      assertEquals(expectedValue, actualValue);
    }
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    // TODO Implement this method to run any cleanup actions needed after every test case
    // glueHelper.purgeDatabase(config.getDatabaseName());
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AwsDatalakeTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return false;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

}
