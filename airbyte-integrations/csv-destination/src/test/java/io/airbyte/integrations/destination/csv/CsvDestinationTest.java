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
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.DataType;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.Stream;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.singer.SingerMessage;
import io.airbyte.singer.SingerMessage.Type;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class CsvDestinationTest {

  private static final ObjectMapper objectMapper = new ObjectMapper();

  private static final String USERS_STREAM_NAME = "users";
  private static final String TASKS_STREAM_NAME = "tasks";
  private static final String USERS_FILE = USERS_STREAM_NAME + ".csv";
  private static final String TASKS_FILE = TASKS_STREAM_NAME + ".csv";
  private static final SingerMessage SINGER_MESSAGE_USERS1 = new SingerMessage().withType(Type.RECORD).withStream(USERS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("name", "john").put("id", "10"));
  private static final SingerMessage SINGER_MESSAGE_USERS2 = new SingerMessage().withType(Type.RECORD).withStream(USERS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("name", "susan").put("id", "30"));
  private static final SingerMessage SINGER_MESSAGE_TASKS1 = new SingerMessage().withType(Type.RECORD).withStream(TASKS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("goal", "announce the game."));
  private static final SingerMessage SINGER_MESSAGE_TASKS2 = new SingerMessage().withType(Type.RECORD).withStream(TASKS_STREAM_NAME)
      .withRecord(objectMapper.createObjectNode().put("goal", "ship some code."));

  private static final Schema CATALOG = new Schema().withStreams(Lists.newArrayList(
      new Stream().withName(USERS_STREAM_NAME)
          .withFields(Lists.newArrayList(new Field().withName("name").withDataType(DataType.STRING).withSelected(true),
              new Field().withName("id").withDataType(DataType.STRING).withSelected(true))),
      new Stream().withName(TASKS_STREAM_NAME)
          .withFields(Lists.newArrayList(new Field().withName("goal").withDataType(DataType.STRING).withSelected(true)))));

  private Path destinationPath;
  private ObjectNode config;

  @BeforeEach
  void setup() throws IOException {
    destinationPath = Files.createTempDirectory("test");
    config = objectMapper.createObjectNode().put(CsvDestination.DESTINATION_PATH_FIELD, destinationPath.toString());
  }

  @Test
  void testSpec() throws IOException {
    final DestinationConnectionSpecification actual = new CsvDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final DestinationConnectionSpecification expected = Jsons.deserialize(resourceString, DestinationConnectionSpecification.class);

    assertEquals(expected, actual);
  }

  @Test
  void testCheckSuccess() {
    final StandardCheckConnectionOutput actual = new CsvDestination().check(config);
    final StandardCheckConnectionOutput expected = new StandardCheckConnectionOutput().withStatus(Status.SUCCESS);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() throws IOException {
    Path looksLikeADirectoryButIsAFile = destinationPath.resolve("file");
    FileUtils.touch(looksLikeADirectoryButIsAFile.toFile());
    final ObjectNode config = objectMapper.createObjectNode().put(CsvDestination.DESTINATION_PATH_FIELD, looksLikeADirectoryButIsAFile.toString());
    final StandardCheckConnectionOutput actual = new CsvDestination().check(config);
    final StandardCheckConnectionOutput expected = new StandardCheckConnectionOutput().withStatus(Status.FAILURE);

    // the message includes the random file path, so just verify it exists and then remove it when we do
    // rest of the comparison.
    assertNotNull(actual.getMessage());
    actual.setMessage(null);
    assertEquals(expected, actual);
  }

  @Test
  void testWriteSuccess() throws Exception {
    final DestinationConsumer<SingerMessage> consumer = new CsvDestination().write(config, CATALOG);

    consumer.accept(SINGER_MESSAGE_USERS1);
    consumer.accept(SINGER_MESSAGE_TASKS1);
    consumer.accept(SINGER_MESSAGE_USERS2);
    consumer.accept(SINGER_MESSAGE_TASKS2);
    consumer.close();

    // verify contents of CSV file
    final List<String> usersActual = Files.readAllLines(destinationPath.resolve(USERS_FILE));
    // csv adds all of these goofy quotes.
    final List<String> usersExpected = Lists.newArrayList(
        CsvDestination.COLUMN_NAME,
        "\"{\"\"name\"\":\"\"john\"\",\"\"id\"\":\"\"10\"\"}\"",
        "\"{\"\"name\"\":\"\"susan\"\",\"\"id\"\":\"\"30\"\"}\"");

    assertEquals(usersExpected, usersActual);

    final List<String> tasksActual = Files.readAllLines(destinationPath.resolve(TASKS_FILE));
    final List<String> tasksExpected = Lists.newArrayList(
        CsvDestination.COLUMN_NAME,
        "\"{\"\"goal\"\":\"\"announce the game.\"\"}\"",
        "\"{\"\"goal\"\":\"\"ship some code.\"\"}\"");

    assertEquals(tasksActual, tasksExpected);

    // verify that the file is parsable as json (sanity check since the quoting is so goofy).
    List<JsonNode> actualUsersJson = csvToJson(destinationPath.resolve(USERS_FILE));
    List<JsonNode> expectedUsersJson = Lists.newArrayList(SINGER_MESSAGE_USERS1.getRecord(), SINGER_MESSAGE_USERS2.getRecord());
    assertEquals(expectedUsersJson, actualUsersJson);

    List<JsonNode> actualTasksJson = csvToJson(destinationPath.resolve(TASKS_FILE));
    List<JsonNode> expectedTasksJson = Lists.newArrayList(SINGER_MESSAGE_TASKS1.getRecord(), SINGER_MESSAGE_TASKS2.getRecord());
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
    final SingerMessage spiedMessage = spy(SINGER_MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getStream();

    final DestinationConsumer<SingerMessage> consumer = spy(new CsvDestination().write(config, CATALOG));

    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(SINGER_MESSAGE_USERS2);
    consumer.close();

    // verify tmp files are cleaned up and no files are output at all
    final Set<String> actualFilenames = Files.list(destinationPath).map(Path::getFileName).map(Path::toString).collect(Collectors.toSet());
    assertEquals(Collections.emptySet(), actualFilenames);
  }

  private List<JsonNode> csvToJson(Path csvPath) throws IOException {
    Reader in = new FileReader(csvPath.toFile());
    Iterable<CSVRecord> records = CSVFormat.DEFAULT
        .withHeader(CsvDestination.COLUMN_NAME)
        .withFirstRecordAsHeader()
        .parse(in);

    final List<JsonNode> jsonRecords = new ArrayList<>();
    for (final CSVRecord record : records) {
      jsonRecords.add(Jsons.deserialize(record.toMap().get(CsvDestination.COLUMN_NAME)));
    }
    return jsonRecords;
  }

}
