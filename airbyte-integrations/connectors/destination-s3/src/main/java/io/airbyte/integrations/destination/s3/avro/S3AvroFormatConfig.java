/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.PART_SIZE_MB_ARG_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import org.apache.avro.file.CodecFactory;

public class S3AvroFormatConfig implements S3FormatConfig {

  private final CodecFactory codecFactory;
  private final Long partSize;

  public S3AvroFormatConfig(final JsonNode formatConfig) {
    this.codecFactory = parseCodecConfig(formatConfig.get("compression_codec"));
    this.partSize = formatConfig.get(PART_SIZE_MB_ARG_NAME) != null ? formatConfig.get(PART_SIZE_MB_ARG_NAME).asLong() : null;
  }

  public static CodecFactory parseCodecConfig(final JsonNode compressionCodecConfig) {
    if (compressionCodecConfig == null || compressionCodecConfig.isNull()) {
      return CodecFactory.nullCodec();
    }

    final JsonNode codecConfig = compressionCodecConfig.get("codec");
    if (codecConfig == null || codecConfig.isNull() || !codecConfig.isTextual()) {
      return CodecFactory.nullCodec();
    }
    final String codecType = codecConfig.asText();
    final CompressionCodec codec = CompressionCodec.fromConfigValue(codecConfig.asText());
    switch (codec) {
      case NULL -> {
        return CodecFactory.nullCodec();
      }
      case DEFLATE -> {
        final int compressionLevel = getCompressionLevel(compressionCodecConfig, 0, 0, 9);
        return CodecFactory.deflateCodec(compressionLevel);
      }
      case BZIP2 -> {
        return CodecFactory.bzip2Codec();
      }
      case XZ -> {
        final int compressionLevel = getCompressionLevel(compressionCodecConfig, 6, 0, 9);
        return CodecFactory.xzCodec(compressionLevel);
      }
      case ZSTANDARD -> {
        final int compressionLevel = getCompressionLevel(compressionCodecConfig, 3, -5, 22);
        final boolean includeChecksum = getIncludeChecksum(compressionCodecConfig, false);
        return CodecFactory.zstandardCodec(compressionLevel, includeChecksum);
      }
      case SNAPPY -> {
        return CodecFactory.snappyCodec();
      }
      default -> {
        throw new IllegalArgumentException("Unsupported compression codec: " + codecType);
      }
    }
  }

  public static int getCompressionLevel(final JsonNode compressionCodecConfig, final int defaultLevel, final int minLevel, final int maxLevel) {
    final JsonNode levelConfig = compressionCodecConfig.get("compression_level");
    if (levelConfig == null || levelConfig.isNull() || !levelConfig.isIntegralNumber()) {
      return defaultLevel;
    }
    final int level = levelConfig.asInt();
    if (level < minLevel || level > maxLevel) {
      throw new IllegalArgumentException(
          String.format("Invalid compression level: %d, expected an integer in range [%d, %d]", level, minLevel, maxLevel));
    }
    return level;
  }

  public static boolean getIncludeChecksum(final JsonNode compressionCodecConfig, final boolean defaultValue) {
    final JsonNode checksumConfig = compressionCodecConfig.get("include_checksum");
    if (checksumConfig == null || checksumConfig.isNumber() || !checksumConfig.isBoolean()) {
      return defaultValue;
    }
    return checksumConfig.asBoolean();
  }

  public CodecFactory getCodecFactory() {
    return codecFactory;
  }

  public Long getPartSize() {
    return partSize;
  }

  @Override
  public S3Format getFormat() {
    return S3Format.AVRO;
  }

  public enum CompressionCodec {

    NULL("no compression"),
    DEFLATE("deflate"),
    BZIP2("bzip2"),
    XZ("xz"),
    ZSTANDARD("zstandard"),
    SNAPPY("snappy");

    private final String configValue;

    CompressionCodec(final String configValue) {
      this.configValue = configValue;
    }

    public static CompressionCodec fromConfigValue(final String configValue) {
      for (final CompressionCodec codec : values()) {
        if (configValue.equalsIgnoreCase(codec.configValue)) {
          return codec;
        }
      }
      throw new IllegalArgumentException("Unknown codec config value: " + configValue);
    }

  }

}
