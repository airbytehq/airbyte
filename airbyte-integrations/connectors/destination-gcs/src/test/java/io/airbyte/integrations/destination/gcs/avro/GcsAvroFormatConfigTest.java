/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.avro;

import static com.amazonaws.services.s3.internal.Constants.MB;
import static org.junit.jupiter.api.Assertions.assertEquals;

import alex.mojaki.s3upload.StreamTransferManager;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.util.ConfigTestUtils;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.integrations.destination.s3.util.S3StreamTransferManagerHelper;
import java.util.List;
import org.apache.avro.file.CodecFactory;
import org.apache.avro.file.DataFileConstants;
import org.apache.commons.lang3.reflect.FieldUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class GcsAvroFormatConfigTest {

  @Test
  public void testParseCodecConfigNull() {
    List<String> nullConfigs = Lists.newArrayList("{}", "{ \"codec\": \"no compression\" }");
    for (String nullConfig : nullConfigs) {
      assertEquals(
          DataFileConstants.NULL_CODEC,
          S3AvroFormatConfig.parseCodecConfig(Jsons.deserialize(nullConfig)).toString());
    }
  }

  @Test
  public void testParseCodecConfigDeflate() {
    // default compression level 0
    CodecFactory codecFactory1 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"deflate\" }"));
    assertEquals("deflate-0", codecFactory1.toString());

    // compression level 5
    CodecFactory codecFactory2 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"deflate\", \"compression_level\": 5 }"));
    assertEquals("deflate-5", codecFactory2.toString());
  }

  @Test
  public void testParseCodecConfigBzip2() {
    JsonNode bzip2Config = Jsons.deserialize("{ \"codec\": \"bzip2\" }");
    CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(bzip2Config);
    assertEquals(DataFileConstants.BZIP2_CODEC, codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigXz() {
    // default compression level 6
    CodecFactory codecFactory1 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"xz\" }"));
    assertEquals("xz-6", codecFactory1.toString());

    // compression level 7
    CodecFactory codecFactory2 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"xz\", \"compression_level\": 7 }"));
    assertEquals("xz-7", codecFactory2.toString());
  }

  @Test
  public void testParseCodecConfigZstandard() {
    // default compression level 3
    CodecFactory codecFactory1 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"zstandard\" }"));
    // There is no way to verify the checksum; all relevant methods are private or protected...
    assertEquals("zstandard[3]", codecFactory1.toString());

    // compression level 20
    CodecFactory codecFactory2 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize(
            "{ \"codec\": \"zstandard\", \"compression_level\": 20, \"include_checksum\": true }"));
    // There is no way to verify the checksum; all relevant methods are private or protected...
    assertEquals("zstandard[20]", codecFactory2.toString());
  }

  @Test
  public void testParseCodecConfigSnappy() {
    JsonNode snappyConfig = Jsons.deserialize("{ \"codec\": \"snappy\" }");
    CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(snappyConfig);
    assertEquals(DataFileConstants.SNAPPY_CODEC, codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigInvalid() {
    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      JsonNode invalidConfig = Jsons.deserialize("{ \"codec\": \"bi-directional-bfs\" }");
      S3AvroFormatConfig.parseCodecConfig(invalidConfig);
    });
  }

  @Test
  public void testHandlePartSizeConfig() throws IllegalAccessException {

    JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"AVRO\",\n"
        + "  \"part_size_mb\": 6\n"
        + "}"));

    GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(gcsDestinationConfig);

    S3FormatConfig formatConfig = gcsDestinationConfig.getFormatConfig();
    assertEquals("AVRO", formatConfig.getFormat().name());
    assertEquals(6, formatConfig.getPartSize());
    // Assert that is set properly in config
    StreamTransferManager streamTransferManager = S3StreamTransferManagerHelper.getDefault(
        gcsDestinationConfig.getBucketName(), "objectKey", null,
        gcsDestinationConfig.getFormatConfig().getPartSize());

    Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * 6, partSizeBytes);
  }

  @Test
  public void testHandleAbsenceOfPartSizeConfig() throws IllegalAccessException {

    JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"AVRO\"\n"
        + "}"));

    GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(gcsDestinationConfig);

    StreamTransferManager streamTransferManager = S3StreamTransferManagerHelper.getDefault(
        gcsDestinationConfig.getBucketName(), "objectKey", null,
        gcsDestinationConfig.getFormatConfig().getPartSize());

    Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * 5, partSizeBytes); // 5MB is a default value if nothing provided explicitly
  }

}
