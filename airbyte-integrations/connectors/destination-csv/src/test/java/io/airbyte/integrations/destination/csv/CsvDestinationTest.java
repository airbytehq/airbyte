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

package io.airbyte.integrations.destination.csv;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class CsvDestinationTest {

  private static final Instant NOW = Instant.now();
  private static final String USERS_STREAM_NAME = "users";
  private static final String TASKS_STREAM_NAME = "tasks";
  private static final String USERS_FILE = USERS_STREAM_NAME + ".csv";
  private static final String TASKS_FILE = TASKS_STREAM_NAME + ".csv";
  private static final AirbyteMessage MESSAGE_USERS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "john").put("id", "10").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_USERS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "susan").put("id", "30").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_TASKS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "announce the game.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_TASKS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "ship some code.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_STATE = new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.builder().put("checkpoint", "now!").build())));

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(
      CatalogHelpers.createAirbyteStream(USERS_STREAM_NAME, Field.of("name", JsonSchemaPrimitive.STRING),
          Field.of("id", JsonSchemaPrimitive.STRING)),
      CatalogHelpers.createAirbyteStream(TASKS_STREAM_NAME, Field.of("goal", JsonSchemaPrimitive.STRING))));

  private Path destinationPath;
  private JsonNode config;

  @BeforeEach
  void setup() throws IOException {
    destinationPath = Files.createTempDirectory("test");
    config = Jsons.jsonNode(ImmutableMap.of(CsvDestination.DESTINATION_PATH_FIELD, destinationPath.toString()));
  }

  @Test
  void testSpec() throws IOException {
    final ConnectorSpecification actual = new CsvDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @Test
  void testCheckSuccess() {
    final AirbyteConnectionStatus actual = new CsvDestination().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() throws IOException {
    final Path looksLikeADirectoryButIsAFile = destinationPath.resolve("file");
    FileUtils.touch(looksLikeADirectoryButIsAFile.toFile());
    final JsonNode config = Jsons.jsonNode(ImmutableMap.of(CsvDestination.DESTINATION_PATH_FIELD, looksLikeADirectoryButIsAFile.toString()));
    final AirbyteConnectionStatus actual = new CsvDestination().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.FAILED);

    // the message includes the random file path, so just verify it exists and then remove it when we do
    // rest of the comparison.
    assertNotNull(actual.getMessage());
    actual.setMessage(null);
    assertEquals(expected, actual);
  }

  @Test
  void testWriteSuccess() throws Exception {
    final DestinationConsumer<AirbyteMessage> consumer = new CsvDestination().write(config, CATALOG);

    consumer.accept(MESSAGE_USERS1);
    consumer.accept(MESSAGE_TASKS1);
    consumer.accept(MESSAGE_USERS2);
    consumer.accept(MESSAGE_TASKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    // verify contents of CSV file
    final String usersActual = Files.readString(destinationPath.resolve(USERS_FILE));
    // csv adds all of these goofy quotes.
    final String EXPECTED_USERS1 = "\"{\"\"name\"\":\"\"john\"\",\"\"id\"\":\"\"10\"\"}\"";
    final String EXPECTED_USERS2 = "\"{\"\"name\"\":\"\"susan\"\",\"\"id\"\":\"\"30\"\"}\"";
    assertTrue(usersActual.contains(EXPECTED_USERS1));
    assertTrue(usersActual.contains(EXPECTED_USERS2));

    final String tasksActual = Files.readString(destinationPath.resolve(TASKS_FILE));
    final String EXPECTED_TASKS1 = "\"{\"\"goal\"\":\"\"announce the game.\"\"}\"";
    final String EXPECTED_TASKS2 = "\"{\"\"goal\"\":\"\"ship some code.\"\"}\"";
    assertTrue(tasksActual.contains(EXPECTED_TASKS1));
    assertTrue(tasksActual.contains(EXPECTED_TASKS2));

    // verify that the file is parsable as json (sanity check since the quoting is so goofy).
    final List<JsonNode> actualUsersJson = csvToJson(destinationPath.resolve(USERS_FILE));
    final List<JsonNode> expectedUsersJson = Lists.newArrayList(MESSAGE_USERS1.getRecord().getData(), MESSAGE_USERS2.getRecord().getData());
    assertEquals(expectedUsersJson, actualUsersJson);

    final List<JsonNode> actualTasksJson = csvToJson(destinationPath.resolve(TASKS_FILE));
    final List<JsonNode> expectedTasksJson = Lists.newArrayList(MESSAGE_TASKS1.getRecord().getData(), MESSAGE_TASKS2.getRecord().getData());
    assertEquals(expectedTasksJson, actualTasksJson);

    // verify tmp files are cleaned up
    final Set<String> actualFilenames = Files.list(destinationPath).map(Path::getFileName).map(Path::toString).collect(Collectors.toSet());
    final Set<String> expectedFilenames = Sets.newHashSet(USERS_FILE, TASKS_FILE);
    assertEquals(expectedFilenames, actualFilenames);
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testWriteFailure() throws Exception {
    // hack to force an exception to be thrown from within the consumer.
    final AirbyteMessage spiedMessage = spy(MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getRecord();

    final DestinationConsumer<AirbyteMessage> consumer = spy(new CsvDestination().write(config, CATALOG));

    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(MESSAGE_USERS2);
    consumer.close();

    // verify tmp files are cleaned up and no files are output at all
    final Set<String> actualFilenames = Files.list(destinationPath).map(Path::getFileName).map(Path::toString).collect(Collectors.toSet());
    assertEquals(Collections.emptySet(), actualFilenames);
  }

  private List<JsonNode> csvToJson(Path csvPath) throws IOException {
    final Reader in = new FileReader(csvPath.toFile());
    final Iterable<CSVRecord> records = CSVFormat.DEFAULT
        .withHeader(CsvDestination.COLUMN_DATA)
        .withFirstRecordAsHeader()
        .parse(in);

    return StreamSupport.stream(records.spliterator(), false)
        .map(record -> Jsons.deserialize(record.toMap().get(CsvDestination.COLUMN_DATA)))
        .collect(Collectors.toList());
  }

}
