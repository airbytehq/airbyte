package io.airbyte.integrations.source.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.bigquery.TempBigQueryJoolDatabaseImpl;
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.nio.file.Files;
import java.nio.file.Path;

public class BigQuerySourceComprehensiveTest extends SourceComprehensiveTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  private static final String CONFIG_DATASET_ID = "dataset_id";
  private static final String CONFIG_PROJECT_ID = "project_id";
  private static final String CONFIG_DATASET_LOCATION = "dataset_location";
  private static final String CONFIG_CREDS = "credentials_json";

  private TempBigQueryJoolDatabaseImpl database;
  private Dataset dataset;
  private boolean tornDown;
  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/source-bigquery:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {

  }

  @Override
  protected Database setupDatabase() throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String credentialsJsonString = new String(Files.readAllBytes(CREDENTIALS_PATH));

    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);
    final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
//    final String datasetLocation = "US";

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, projectId)
        .put(CONFIG_CREDS, credentialsJsonString)
        .put(CONFIG_DATASET_ID, datasetId)
//        .put(CONFIG_DATASET_LOCATION, datasetLocation)
        .build());

    database = new TempBigQueryJoolDatabaseImpl(config.get(CONFIG_PROJECT_ID).asText(), credentialsJsonString);

    final DatasetInfo datasetInfo =
        DatasetInfo.newBuilder(config.get(CONFIG_DATASET_ID).asText()).setLocation(config.get(CONFIG_DATASET_LOCATION).asText()).build();
    dataset = database.getRealDatabase().getBigQuery().create(datasetInfo);
    return database;
  }

  @Override
  protected void initTests() {

  }

  @Override
  protected String getNameSpace() {
    return dataset.getFriendlyName();
  }
}
