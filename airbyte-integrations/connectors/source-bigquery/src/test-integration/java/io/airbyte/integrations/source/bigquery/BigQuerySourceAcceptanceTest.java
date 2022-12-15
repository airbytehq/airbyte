/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static io.airbyte.integrations.source.bigquery.BigQuerySource.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.bigquery.BigQueryDatabase;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.HashMap;

public class BigQuerySourceAcceptanceTest extends SourceAcceptanceTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private static final String STREAM_NAME = "id_and_name";

  private BigQueryDatabase database;
  private Dataset dataset;
  private JsonNode config;

  @Override
  protected void setupEnvironment(final TestDestinationEnv testEnv) throws IOException, SQLException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);

    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);
    final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
    final String datasetLocation = "US";

    final String datasetId = Strings.addRandomSuffix("airbyte_tests_acceptance", "_", 8);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, projectId)
        .put(CONFIG_CREDS, credentialsJsonString)
        .put(CONFIG_DATASET_ID, datasetId)
        .build());

    database = new BigQueryDatabase(config.get(CONFIG_PROJECT_ID).asText(), credentialsJsonString);

    final DatasetInfo datasetInfo =
        DatasetInfo.newBuilder(config.get(CONFIG_DATASET_ID).asText()).setLocation(datasetLocation).build();
    dataset = database.getBigQuery().create(datasetInfo);

    database.execute("CREATE TABLE " + datasetId + ".id_and_name(id INT64, name STRING);");
    database.execute("INSERT INTO " + datasetId + ".id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    database.cleanDataSet(dataset.getDatasetId().getDataset());
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-bigquery:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.createConfiguredAirbyteCatalog(
        STREAM_NAME,
        config.get(CONFIG_DATASET_ID).asText(),
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("name", JsonSchemaType.STRING));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
