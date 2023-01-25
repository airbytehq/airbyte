/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.AIRBYTE_COLUMNS;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.CONFIG_PROJECT_ID;
import static io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedTestConstants.NAME_TRANSFORMER;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.configureBigQuery;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.createCommonConfig;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.getBigQueryDataSet;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestDataUtils.tearDownBigQuery;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.ConnectionProperty;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableResult;
import com.google.common.collect.Streams;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.bigquery.BigQueryResultSet;
import io.airbyte.db.bigquery.BigQuerySourceOperations;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.argproviders.DataArgumentsProvider;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.TimeZone;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedDestinationAcceptanceTest.class);

  private BigQuery bigquery;
  private Dataset dataset;
  private JsonNode config;
  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-bigquery-denormalized:dev";
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
  protected Optional<NamingConventionTransformer> getNameTransformer() {
    return Optional.of(NAME_TRANSFORMER);
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new BigQueryDenormalizedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  // #13154 Normalization issue
  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected void assertNamespaceNormalization(final String testCaseId,
                                              final String expectedNormalizedNamespace,
                                              final String actualNormalizedNamespace) {
    final String message = String.format("Test case %s failed; if this is expected, please override assertNamespaceNormalization", testCaseId);
    if (testCaseId.equals("S3A-1")) {
      // bigquery allows namespace starting with a number, and prepending underscore
      // will hide the dataset, so we don't do it as we do for other destinations
      assertEquals("99namespace", actualNormalizedNamespace, message);
    } else {
      assertEquals(expectedNormalizedNamespace, actualNormalizedNamespace, message);
    }
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    return BigQueryUtils.getDatasetId(config);
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    final String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    final String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schema) throws InterruptedException {
    TimeZone.setDefault(TimeZone.getTimeZone("UTC"));

    final QueryJobConfiguration queryConfig =
        QueryJobConfiguration
            .newBuilder(
                String.format("SELECT * FROM `%s`.`%s` order by %s asc;", schema, tableName,
                    JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            // .setUseLegacySql(false)
            .setConnectionProperties(Collections.singletonList(ConnectionProperty.of("time_zone", "UTC")))
            .build();

    final TableResult queryResults = executeQuery(bigquery, queryConfig).getLeft().getQueryResults();
    final FieldList fields = queryResults.getSchema().getFields();
    final BigQuerySourceOperations sourceOperations = new BigQuerySourceOperations();

    return Streams.stream(queryResults.iterateAll())
        .map(fieldValues -> sourceOperations.rowToJson(new BigQueryResultSet(fieldValues, fields))).collect(Collectors.toList());
  }

  private boolean isAirbyteColumn(final String name) {
    if (AIRBYTE_COLUMNS.contains(name)) {
      return true;
    }
    return name.startsWith("_airbyte") && name.endsWith("_hashid");
  }

  private Object getTypedFieldValue(final FieldValueList row, final Field field) {
    final FieldValue fieldValue = row.get(field.getName());
    if (fieldValue.getValue() != null) {
      return switch (field.getType().getStandardType()) {
        case FLOAT64, NUMERIC -> fieldValue.getDoubleValue();
        case INT64 -> fieldValue.getNumericValue().intValue();
        case STRING -> fieldValue.getStringValue();
        case BOOL -> fieldValue.getBooleanValue();
        case STRUCT -> fieldValue.getRecordValue().toString();
        default -> fieldValue.getValue();
      };
    } else {
      return null;
    }
  }

  protected JsonNode createConfig() throws IOException {
    return createCommonConfig();
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    config = createConfig();
    bigquery = configureBigQuery(config);
    dataset = getBigQueryDataSet(config, bigquery);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    tearDownBigQuery(dataset, bigquery);
  }

  // todo (cgardens) - figure out how to share these helpers. they are currently copied from
  // BigQueryDestination.
  private static ImmutablePair<Job, String> executeQuery(final BigQuery bigquery, final QueryJobConfiguration queryConfig) {
    final JobId jobId = JobId.of(UUID.randomUUID().toString());
    final Job queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build());
    return executeQuery(queryJob);
  }

  private static ImmutablePair<Job, String> executeQuery(final Job queryJob) {
    final Job completedJob = waitForQuery(queryJob);
    if (completedJob == null) {
      throw new RuntimeException("Job no longer exists");
    } else if (completedJob.getStatus().getError() != null) {
      // You can also look at queryJob.getStatus().getExecutionErrors() for all
      // errors, not just the latest one.
      return ImmutablePair.of(null, (completedJob.getStatus().getError().toString()));
    }

    return ImmutablePair.of(completedJob, null);
  }

  private static Job waitForQuery(final Job queryJob) {
    try {
      return queryJob.waitFor();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Verify that the integration successfully writes normalized records successfully (without actually
   * running the normalization module) Tests a wide variety of messages an schemas (aspirationally,
   * anyway).
   */
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncNormalizedWithoutNormalization(final String messagesFilename, final String catalogFilename) throws Exception {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());

    final JsonNode config = getConfig();
    // don't run normalization though
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);

    final String defaultSchema = getDefaultSchema(config);
    final List<AirbyteRecordMessage> actualMessages = retrieveNormalizedRecords(catalog, defaultSchema);
    assertSameMessages(messages, actualMessages, true);
  }

}
