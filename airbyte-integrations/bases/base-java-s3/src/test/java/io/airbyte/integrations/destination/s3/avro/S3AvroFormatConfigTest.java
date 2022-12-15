/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import static com.amazonaws.services.s3.internal.Constants.MB;
import static io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import alex.mojaki.s3upload.StreamTransferManager;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.StorageProvider;
import io.airbyte.integrations.destination.s3.util.ConfigTestUtils;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
import java.util.List;
import org.apache.avro.file.CodecFactory;
import org.apache.avro.file.DataFileConstants;
import org.apache.commons.lang3.reflect.FieldUtils;
import org.junit.jupiter.api.Test;

class S3AvroFormatConfigTest {

  @Test
  public void testParseCodecConfigNull() {
    final List<String> nullConfigs = Lists.newArrayList("{}", "{ \"codec\": \"no compression\" }");
    for (final String nullConfig : nullConfigs) {
      assertEquals(
          DataFileConstants.NULL_CODEC,
          S3AvroFormatConfig.parseCodecConfig(Jsons.deserialize(nullConfig)).toString());
    }
  }

  @Test
  public void testParseCodecConfigDeflate() {
    // default compression level 0
    final CodecFactory codecFactory1 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"deflate\" }"));
    assertEquals("deflate-0", codecFactory1.toString());

    // compression level 5
    final CodecFactory codecFactory2 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"deflate\", \"compression_level\": 5 }"));
    assertEquals("deflate-5", codecFactory2.toString());
  }

  @Test
  public void testParseCodecConfigBzip2() {
    final JsonNode bzip2Config = Jsons.deserialize("{ \"codec\": \"bzip2\" }");
    final CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(bzip2Config);
    assertEquals(DataFileConstants.BZIP2_CODEC, codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigXz() {
    // default compression level 6
    final CodecFactory codecFactory1 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"xz\" }"));
    assertEquals("xz-6", codecFactory1.toString());

    // compression level 7
    final CodecFactory codecFactory2 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"xz\", \"compression_level\": 7 }"));
    assertEquals("xz-7", codecFactory2.toString());
  }

  @Test
  public void testParseCodecConfigZstandard() {
    // default compression level 3
    final CodecFactory codecFactory1 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize("{ \"codec\": \"zstandard\" }"));
    // There is no way to verify the checksum; all relevant methods are private or protected...
    assertEquals("zstandard[3]", codecFactory1.toString());

    // compression level 20
    final CodecFactory codecFactory2 = S3AvroFormatConfig.parseCodecConfig(
        Jsons.deserialize(
            "{ \"codec\": \"zstandard\", \"compression_level\": 20, \"include_checksum\": true }"));
    // There is no way to verify the checksum; all relevant methods are private or protected...
    assertEquals("zstandard[20]", codecFactory2.toString());
  }

  @Test
  public void testParseCodecConfigSnappy() {
    final JsonNode snappyConfig = Jsons.deserialize("{ \"codec\": \"snappy\" }");
    final CodecFactory codecFactory = S3AvroFormatConfig.parseCodecConfig(snappyConfig);
    assertEquals(DataFileConstants.SNAPPY_CODEC, codecFactory.toString());
  }

  @Test
  public void testParseCodecConfigInvalid() {
    try {
      final JsonNode invalidConfig = Jsons.deserialize("{ \"codec\": \"bi-directional-bfs\" }");
      S3AvroFormatConfig.parseCodecConfig(invalidConfig);
      fail();
    } catch (final IllegalArgumentException e) {
      // expected
    }
  }

  @Test
  public void testHandlePartSizeConfig() throws IllegalAccessException {

    final JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"AVRO\"\n"
        + "}"));

    final S3DestinationConfig s3DestinationConfig = S3DestinationConfig
        .getS3DestinationConfig(config, StorageProvider.AWS_S3);
    ConfigTestUtils.assertBaseConfig(s3DestinationConfig);

    final S3FormatConfig formatConfig = s3DestinationConfig.getFormatConfig();
    assertEquals("AVRO", formatConfig.getFormat().name());
    // Assert that is set properly in config
    final StreamTransferManager streamTransferManager = StreamTransferManagerFactory
        .create(s3DestinationConfig.getBucketName(), "objectKey", null)
        .get();

    final Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * DEFAULT_PART_SIZE_MB, partSizeBytes);
  }

  @Test
  public void testHandleAbsenceOfPartSizeConfig() throws IllegalAccessException {

    final JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"AVRO\"\n"
        + "}"));

    final S3DestinationConfig s3DestinationConfig = S3DestinationConfig
        .getS3DestinationConfig(config, StorageProvider.AWS_S3);
    ConfigTestUtils.assertBaseConfig(s3DestinationConfig);

    final StreamTransferManager streamTransferManager = StreamTransferManagerFactory
        .create(s3DestinationConfig.getBucketName(), "objectKey", null)
        .get();

    final Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * DEFAULT_PART_SIZE_MB, partSizeBytes);
  }

}
