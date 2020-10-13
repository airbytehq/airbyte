/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.bigquery;

import static java.util.stream.Collectors.toList;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.config.DataType;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.Stream;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.singer.SingerMessage;
import io.airbyte.singer.SingerMessage.Type;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class BigQueryDestinationTest {

  private static final Path CREDENTIALS_PATH = Path.of("config/credentials.json");

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestinationTest.class);

  private static final ObjectMapper objectMapper = new ObjectMapper();

  private static final String USERS_STREAM_NAME = "users";
  private static final String TASKS_STREAM_NAME = "tasks";
  private static final SingerMessage SINGER_MESSAGE_USERS1 = new SingerMessage().withType(Type.RECORD).withStream(USERS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("name", "john").put("id", "10"));
  private static final SingerMessage SINGER_MESSAGE_USERS2 = new SingerMessage().withType(Type.RECORD).withStream(USERS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("name", "susan").put("id", "30"));
  private static final SingerMessage SINGER_MESSAGE_TASKS1 = new SingerMessage().withType(Type.RECORD).withStream(TASKS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("goal", "announce the game."));
  private static final SingerMessage SINGER_MESSAGE_TASKS2 = new SingerMessage().withType(Type.RECORD).withStream(TASKS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("goal", "ship some code."));
  private static final SingerMessage STATE_MESSAGE = new SingerMessage().withType(Type.STATE)
      .withValue(objectMapper.createObjectNode().put("checkpoint", "now!"));

  private static final Schema CATALOG = new Schema().withStreams(Lists.newArrayList(
      new Stream().withName(USERS_STREAM_NAME)
          .withFields(Lists.newArrayList(new Field().withName("name").withDataType(DataType.STRING).withSelected(true),
              new Field().withName("id").withDataType(DataType.STRING).withSelected(true))),
      new Stream().withName(TASKS_STREAM_NAME)
          .withFields(Lists.newArrayList(new Field().withName("goal").withDataType(DataType.STRING).withSelected(true)))));

  private JsonNode config;

  private BigQuery bigquery;
  private Dataset dataset;

  private boolean tornDown = true;

  @BeforeEach
  void setup(TestInfo info) throws IOException {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/config/credentials.json. Override by setting setting path with the CREDENTIALS_PATH constant.");
    }
    final String credentialsJsonString = new String(Files.readAllBytes(CREDENTIALS_PATH));
    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);

    final String projectId = credentialsJson.get(BigQueryDestination.CONFIG_PROJECT_ID).asText();
    final ServiceAccountCredentials credentials = ServiceAccountCredentials.fromStream(new ByteArrayInputStream(credentialsJsonString.getBytes()));
    bigquery = BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(credentials)
        .build()
        .getService();

    final String datasetId = "airbyte_tests_" + RandomStringUtils.randomAlphanumeric(8);

    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).build();
    dataset = bigquery.create(datasetInfo);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryDestination.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryDestination.CONFIG_CREDS, credentialsJsonString)
        .put(BigQueryDestination.CONFIG_DATASET_ID, datasetId)
        .build());

    tornDown = false;
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  if (!tornDown) {
                    tearDownBigQuery();
                  }
                }));

  }

  @AfterEach
  void tearDown(TestInfo info) {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    tearDownBigQuery();
  }

  private void tearDownBigQuery() {
    // allows deletion of a dataset that has contents
    final BigQuery.DatasetDeleteOption option = BigQuery.DatasetDeleteOption.deleteContents();

    final boolean success = bigquery.delete(dataset.getDatasetId(), option);
    if (success) {
      LOGGER.info("BQ Dataset " + dataset + " deleted...");
    } else {
      LOGGER.info("BQ Dataset cleanup for " + dataset + " failed!");
    }

    tornDown = true;
  }

  // todo - same test as csv destination
  @Test
  void testSpec() throws IOException {
    final ConnectorSpecification actual = new BigQueryDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  // todo - same test as csv destination
  @Test
  void testCheckSuccess() {
    final StandardCheckConnectionOutput actual = new BigQueryDestination().check(config);
    final StandardCheckConnectionOutput expected = new StandardCheckConnectionOutput().withStatus(Status.SUCCESS);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() {
    ((ObjectNode) config).put(BigQueryDestination.CONFIG_PROJECT_ID, "fake");
    final StandardCheckConnectionOutput actual = new BigQueryDestination().check(config);
    final StandardCheckConnectionOutput expected = new StandardCheckConnectionOutput().withStatus(Status.FAILURE)
        .withMessage("Access Denied: Project fake: User does not have bigquery.jobs.create permission in project fake.");
    assertEquals(expected, actual);
  }

  @Test
  void testWriteSuccess() throws Exception {
    final DestinationConsumer<SingerMessage> consumer = new BigQueryDestination().write(config, CATALOG);

    consumer.accept(SINGER_MESSAGE_USERS1);
    consumer.accept(SINGER_MESSAGE_TASKS1);
    consumer.accept(SINGER_MESSAGE_USERS2);
    consumer.accept(SINGER_MESSAGE_TASKS2);
    consumer.accept(STATE_MESSAGE);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecords(USERS_STREAM_NAME);
    final List<JsonNode> expectedUsersJson = Lists.newArrayList(SINGER_MESSAGE_USERS1.getRecord(), SINGER_MESSAGE_USERS2.getRecord());
    assertEquals(expectedUsersJson.size(), usersActual.size());
    assertTrue(expectedUsersJson.containsAll(usersActual) && usersActual.containsAll(expectedUsersJson));

    final List<JsonNode> tasksActual = retrieveRecords(TASKS_STREAM_NAME);
    final List<JsonNode> expectedTasksJson = Lists.newArrayList(SINGER_MESSAGE_TASKS1.getRecord(), SINGER_MESSAGE_TASKS2.getRecord());
    assertEquals(expectedTasksJson.size(), tasksActual.size());
    assertTrue(expectedTasksJson.containsAll(tasksActual) && tasksActual.containsAll(expectedTasksJson));

    assertTmpTablesNotPresent(CATALOG.getStreams().stream().map(Stream::getName).collect(Collectors.toList()));
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testWriteFailure() throws Exception {
    // hack to force an exception to be thrown from within the consumer.
    final SingerMessage spiedMessage = spy(SINGER_MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getStream();

    final DestinationConsumer<SingerMessage> consumer = spy(new BigQueryDestination().write(config, CATALOG));

    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(SINGER_MESSAGE_USERS2);
    consumer.close();

    final List<String> tableNames = CATALOG.getStreams().stream().map(Stream::getName).collect(toList());
    assertTmpTablesNotPresent(CATALOG.getStreams().stream().map(Stream::getName).collect(Collectors.toList()));
    // assert that no tables were created.
    assertTrue(fetchNamesOfTablesInDb().stream().noneMatch(tableName -> tableNames.stream().anyMatch(tableName::startsWith)));
  }

  private Set<String> fetchNamesOfTablesInDb() throws InterruptedException {
    final QueryJobConfiguration queryConfig = QueryJobConfiguration
        .newBuilder(String.format("SELECT * FROM %s.INFORMATION_SCHEMA.TABLES;", dataset.getDatasetId().getDataset()))
        .setUseLegacySql(false)
        .build();

    return StreamSupport
        .stream(BigQueryDestination.executeQuery(bigquery, queryConfig).getLeft().getQueryResults().iterateAll().spliterator(), false)
        .map(v -> v.get("TABLE_NAME").getStringValue()).collect(Collectors.toSet());
  }

  private void assertTmpTablesNotPresent(List<String> tableNames) throws InterruptedException {
    final Set<String> tmpTableNamePrefixes = tableNames.stream().map(name -> name + "_").collect(Collectors.toSet());
    assertTrue(fetchNamesOfTablesInDb().stream().noneMatch(tableName -> tmpTableNamePrefixes.stream().anyMatch(tableName::startsWith)));
  }

  private List<JsonNode> retrieveRecords(String tableName) throws Exception {
    QueryJobConfiguration queryConfig =
        QueryJobConfiguration.newBuilder(String.format("SELECT * FROM %s.%s;", dataset.getDatasetId().getDataset(), tableName.toLowerCase()))
            .setUseLegacySql(false).build();

    BigQueryDestination.executeQuery(bigquery, queryConfig);

    return StreamSupport
        .stream(BigQueryDestination.executeQuery(bigquery, queryConfig).getLeft().getQueryResults().iterateAll().spliterator(), false)
        .map(v -> v.get(BigQueryDestination.COLUMN_DATA).getStringValue())
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

}
