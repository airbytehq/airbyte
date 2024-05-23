/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQuery.DatasetDeleteOption;
import com.google.cloud.bigquery.BigQuery.DatasetListOption;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.ConnectionProperty;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableResult;
import com.google.common.collect.Streams;
import io.airbyte.cdk.db.bigquery.BigQueryResultSet;
import io.airbyte.cdk.db.bigquery.BigQuerySourceOperations;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.TestingNamespaces;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.TimeZone;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Disabled
public abstract class AbstractBigQueryDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final NamingConventionTransformer NAME_TRANSFORMER = new BigQuerySQLNameTransformer();
  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractBigQueryDestinationAcceptanceTest.class);

  protected static final String CONFIG_PROJECT_ID = "project_id";
  protected Path secretsFile;
  protected BigQuery bigquery;
  protected Dataset dataset;

  protected JsonNode config;
  protected final StandardNameTransformer namingResolver = new StandardNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-bigquery:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    ((ObjectNode) config).put(CONFIG_PROJECT_ID, "fake");
    return config;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected boolean supportNamespaceTest() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new BigQueryTestDataComparator();
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
  protected boolean supportIncrementalSchemaChanges() {
    return true;
  }

  @Override
  protected Optional<NamingConventionTransformer> getNameTransformer() {
    return Optional.of(NAME_TRANSFORMER);
  }

  @Override
  protected void assertNamespaceNormalization(final String testCaseId,
                                              final String expectedNormalizedNamespace,
                                              final String actualNormalizedNamespace) {
    final String message = String.format("Test case %s failed; if this is expected, please override assertNamespaceNormalization", testCaseId);
    if (testCaseId.equals("S3A-1")) {
      /*
       * See NamespaceTestCaseProvider for how this suffix is generated. <p> expectedNormalizedNamespace
       * will look something like this: `_99namespace_test_20230824_bicrt`. We want to grab the part after
       * `_99namespace`.
       */
      final int underscoreIndex = expectedNormalizedNamespace.indexOf("_", 1);
      final String randomSuffix = expectedNormalizedNamespace.substring(underscoreIndex);
      /*
       * bigquery allows originalNamespace starting with a number, and prepending underscore will hide the
       * dataset, so we don't do it as we do for other destinations
       */
      assertEquals("99namespace" + randomSuffix, actualNormalizedNamespace, message);
    } else {
      assertEquals(expectedNormalizedNamespace, actualNormalizedNamespace, message);
    }
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    return BigQueryUtils.getDatasetId(config);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final StreamId streamId =
        new BigQuerySqlGenerator(null, null).buildStreamId(namespace, streamName, JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE);
    return retrieveRecordsFromTable(streamId.getRawName(), streamId.getRawNamespace())
        .stream()
        .map(node -> node.get(JavaBaseConstants.COLUMN_NAME_DATA).asText())
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

  protected List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schema) throws InterruptedException {
    TimeZone.setDefault(TimeZone.getTimeZone("UTC"));

    final QueryJobConfiguration queryConfig =
        QueryJobConfiguration
            .newBuilder(
                String.format("SELECT * FROM `%s`.`%s` order by %s asc;", schema, tableName,
                    JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT))
            .setUseLegacySql(false)
            .setConnectionProperties(Collections.singletonList(ConnectionProperty.of("time_zone", "UTC")))
            .build();

    final TableResult queryResults = BigQueryUtils.executeQuery(bigquery, queryConfig).getLeft().getQueryResults();
    final FieldList fields = queryResults.getSchema().getFields();
    final BigQuerySourceOperations sourceOperations = new BigQuerySourceOperations();

    return Streams.stream(queryResults.iterateAll())
        .map(fieldValues -> sourceOperations.rowToJson(new BigQueryResultSet(fieldValues, fields))).collect(Collectors.toList());
  }

  protected void setUpBigQuery() throws IOException {
    // secrets file should be set by the inhereting class
    Assertions.assertNotNull(secretsFile);
    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);
    final String stagingPathSuffix = Strings.addRandomSuffix("test_path", "_", 8);
    config = BigQueryDestinationTestUtils.createConfig(secretsFile, datasetId, stagingPathSuffix);

    final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    bigquery = BigQueryDestinationTestUtils.initBigQuery(config, projectId);
    dataset = BigQueryDestinationTestUtils.initDataSet(config, bigquery, datasetId);
  }

  protected void removeOldNamespaces() {
    int datasetsDeletedCount = 0;
    // todo (cgardens) - hardcoding to testing project to de-risk this running somewhere unexpected.
    for (final Dataset dataset1 : bigquery.listDatasets("dataline-integration-testing", DatasetListOption.all())
        .iterateAll()) {
      if (TestingNamespaces.isOlderThan2Days(dataset1.getDatasetId().getDataset())) {
        try {
          bigquery.delete(dataset1.getDatasetId(), DatasetDeleteOption.deleteContents());
          datasetsDeletedCount++;
        } catch (final BigQueryException e) {
          LOGGER.error("Failed to delete old dataset: {}", dataset1.getDatasetId().getDataset(), e);
        }
      }
    }
    LOGGER.info("Deleted {} old datasets.", datasetsDeletedCount);
  }

  protected void tearDownBigQuery() {
    BigQueryDestinationTestUtils.tearDownBigQuery(bigquery, dataset, LOGGER);
  }

}
