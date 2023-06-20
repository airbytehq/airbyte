package io.airbyte.integrations.source.kafka.converter;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import org.junit.jupiter.api.Test;

class JsonConverterTest {

  @Test
  void testConvertToAirbyteRecord() throws JsonProcessingException {
    String recordString = """
        {
           "name": "Team",
           "surname": "Member",
           "age": 42
        }
        """;

    ObjectMapper mapper = new ObjectMapper();
    JsonNode testRecord = mapper.readTree(recordString);

    String testTopic = "test_topic";

    Converter<JsonNode> converter = new JsonConverter();

    AirbyteRecordMessage actualMessage = converter.convertToAirbyteRecord(testTopic, testRecord);

    assertAll(
        () -> assertEquals(testTopic, actualMessage.getStream()),
        () -> assertEquals(testRecord, actualMessage.getData())
    );
  }
}