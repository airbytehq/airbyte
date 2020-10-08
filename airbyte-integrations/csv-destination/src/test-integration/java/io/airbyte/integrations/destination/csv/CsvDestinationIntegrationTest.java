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

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.TestDestination;
import java.io.FileReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;

public class CsvDestinationIntegrationTest extends TestDestination {

  private static final String IMAGE_NAME = "airbyte/airbyte-csv-destination:dev";
  private static final Path RELATIVE_PATH = Path.of("integration_test/charles");
  private static final JsonNode CONFIG = new ObjectMapper().createObjectNode()
      .put("destination_path", Path.of("/local").resolve(RELATIVE_PATH).toString());

  public CsvDestinationIntegrationTest() {
    super(new TestDestinationConfig.Builder(IMAGE_NAME, CONFIG, getSingerMessagesFunction()).build());
  }

  static CheckedFunction<TestDestinationEnv, List<JsonNode>, Exception> getSingerMessagesFunction() {
    return (testEnv) -> {
      final List<Path> list = Files.list(testEnv.getLocalRoot().resolve(RELATIVE_PATH)).collect(Collectors.toList());
      assertEquals(1, list.size());

      final FileReader in = new FileReader(list.get(0).toFile());
      final Iterable<CSVRecord> records = CSVFormat.DEFAULT
          .withHeader(CsvDestination.COLUMN_NAME)
          .withFirstRecordAsHeader()
          .parse(in);

      return StreamSupport.stream(records.spliterator(), false)
          .map(record -> Jsons.deserialize(record.toMap().get(CsvDestination.COLUMN_NAME)))
          .collect(Collectors.toList());
    };
  }

}
