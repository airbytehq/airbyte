package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import java.util.List;
import org.apache.avro.file.CodecFactory;
import org.apache.avro.file.DataFileConstants;
import org.junit.jupiter.api.Test;

class S3AvroFormatConfigTest {

  @Test
  public void testParseCodecConfigNull() {
    List<String> nullConfigs = Lists.newArrayList("{}", "{ \"codec\": \"no compression\" }");
    for (String nullConfig : nullConfigs) {
      assertEquals(
          DataFileConstants.NULL_CODEC,
          S3AvroFormatConfig.parseCodecConfig(Jsons.deserialize(nullConfig)).toString()
      );
    }
  }

  @Test
  public void testParseCodecConfigDeflate() {
    JsonNode deflateConfig = Jsons.deserialize("{ \"codec\": \"deflate\", \"compression_level\": 5 }");
    CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(deflateConfig);
    assertEquals("deflate-5", codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigBzip2() {
    JsonNode bzip2Config = Jsons.deserialize("{ \"codec\": \"bzip2\" }");
    CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(bzip2Config);
    assertEquals(DataFileConstants.BZIP2_CODEC, codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigXz() {
    JsonNode xzConfig = Jsons.deserialize("{ \"codec\": \"xz\", \"compression_level\": 7 }");
    CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(xzConfig);
    assertEquals("xz-7", codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigZstandard() {
    JsonNode zstandardConfig = Jsons.deserialize("{ \"codec\": \"zstandard\", \"compression_level\": 20, \"include_checksum\": true }");
    CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(zstandardConfig);
    // There is no way to verify the checksum; all relevant methods are private or protected...
    assertEquals("zstandard[20]", codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigSnappy() {
    JsonNode snappyConfig = Jsons.deserialize("{ \"codec\": \"snappy\" }");
    CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(snappyConfig);
    assertEquals(DataFileConstants.SNAPPY_CODEC, codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigInvalid() {
    try {
      JsonNode invalidConfig = Jsons.deserialize("{ \"codec\": \"bi-directional-bfs\" }");
      S3AvroFormatConfig.parseCodecConfig(invalidConfig);
      fail();
    } catch (IllegalArgumentException e) {
      // expected
    }
  }

}
