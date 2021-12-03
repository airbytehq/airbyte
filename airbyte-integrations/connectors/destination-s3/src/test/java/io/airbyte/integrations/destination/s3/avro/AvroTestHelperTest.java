package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import org.junit.jupiter.api.Test;

class AvroTestHelperTest {

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();

  @Test
  public void testParseDateValue() {
    assertEquals("20210101", AvroTestHelper.parseDateValue(MAPPER.getNodeFactory().textNode("20210101")));
    assertEquals("invalid_date", AvroTestHelper.parseDateValue(MAPPER.getNodeFactory().textNode("invalid_date")));
    assertEquals("20210101", AvroTestHelper.parseDateValue(MAPPER.getNodeFactory().textNode("2021-01-01")));
    assertEquals("20210101", AvroTestHelper.parseDateValue(MAPPER.getNodeFactory().numberNode(18628)));
  }

}
