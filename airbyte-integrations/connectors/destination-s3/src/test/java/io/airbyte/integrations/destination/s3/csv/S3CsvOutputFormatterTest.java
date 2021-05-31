package io.airbyte.integrations.destination.s3.csv;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertLinesMatch;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.protocol.models.AirbyteStream;
import java.sql.Timestamp;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("S3CsvOutputFormatter")
class S3CsvOutputFormatterTest {

  private static final ObjectMapper mapper = new ObjectMapper();

  @Test
  @DisplayName("getSortedFields")
  public void testGetSortedFields() {
    List<String> fields = Lists.newArrayList("C", "B", "A", "c", "b", "a");
    Collections.shuffle(fields);

    ObjectNode schemaProperties = mapper.createObjectNode();
    for (String field : fields) {
      schemaProperties.set(field, mapper.createObjectNode());
    }
    ObjectNode schema = mapper.createObjectNode();
    schema.set("properties", schemaProperties);

    // No flattening
    S3CsvFormatConfig formatConfig1 = new S3CsvFormatConfig(Flattening.NO);
    assertLinesMatch(Collections.emptyList(),
        S3CsvOutputFormatter.getSortedFields(schema, formatConfig1));

    // Root level flattening
    S3CsvFormatConfig formatConfig2 = new S3CsvFormatConfig(Flattening.ROOT_LEVEL);
    List<String> sortedFields = fields.stream().sorted().collect(Collectors.toList());
    assertLinesMatch(sortedFields, S3CsvOutputFormatter.getSortedFields(schema, formatConfig2));
  }

  @Test
  @DisplayName("getOutputPrefix")
  public void testGetOutputPrefix() {
    // No namespace
    assertEquals("bucket_path/stream_name", S3CsvOutputFormatter
        .getOutputPrefix("bucket_path", new AirbyteStream().withName("stream_name"))
    );

    // With namespace
    assertEquals("bucket_path/namespace/stream_name", S3CsvOutputFormatter
        .getOutputPrefix("bucket_path",
            new AirbyteStream().withNamespace("namespace").withName("stream_name")));
  }

  @Test
  @DisplayName("getOutputFilename")
  public void testGetOutputFilename() {
    Timestamp timestamp = new Timestamp(1471461319000L);
    assertEquals(
        "2016-08-17-1471461319000.csv",
        S3CsvOutputFormatter.getOutputFilename(timestamp)
    );
  }

  @Test
  @DisplayName("getHeaders")
  public void testGetHeaders() {
    // Without sorted headers
    assertLinesMatch(
        Lists.newArrayList(
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            JavaBaseConstants.COLUMN_NAME_DATA),
        S3CsvOutputFormatter.getHeaders(Collections.emptyList())
    );

    // With sorted headers
    assertLinesMatch(
        Lists.newArrayList(
            JavaBaseConstants.COLUMN_NAME_AB_ID,
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            "Field 1",
            "Field 2"),
        S3CsvOutputFormatter.getHeaders(Lists.newArrayList("Field 1", "Field 2"))
    );
  }

  @Test
  @DisplayName("getCsvData")
  public void testGetCsvData() {
    ObjectNode json = mapper.createObjectNode();
    json.set("Field 4", mapper.createObjectNode().put("Field 41", 15));
    json.put("Field 1", "A");
    json.put("Field 3", 71);
    json.put("Field 2", true);
    System.out.println(json.toPrettyString());

    // No flattening
    S3CsvFormatConfig formatConfig1 = new S3CsvFormatConfig(Flattening.NO);
    assertLinesMatch(
        Collections
            .singletonList("{\"Field 4\":{\"Field 41\":15},\"Field 1\":\"A\",\"Field 3\":71,\"Field 2\":true}"),
        S3CsvOutputFormatter.getCsvData(formatConfig1, Collections.emptyList(), json)
    );
    // Root level flattening
    S3CsvFormatConfig formatConfig2 = new S3CsvFormatConfig(Flattening.ROOT_LEVEL);
    assertLinesMatch(
        Lists.newArrayList("A", "true", "71", "{\"Field 41\":15}"),
        S3CsvOutputFormatter
            .getCsvData(formatConfig2, Lists.newArrayList("Field 1", "Field 2", "Field 3", "Field 4"), json)
    );
  }

}
