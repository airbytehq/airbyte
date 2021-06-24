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

package io.airbyte.integrations.destination.s3.avro;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import org.apache.avro.file.CodecFactory;

public class S3AvroFormatConfig implements S3FormatConfig {

  private final CodecFactory codecFactory;

  public S3AvroFormatConfig(JsonNode formatConfig) {
    this.codecFactory = parseCodecConfig(formatConfig.get("compression_codec"));
  }

  public static CodecFactory parseCodecConfig(JsonNode compressionCodecConfig) {
    if (compressionCodecConfig == null || compressionCodecConfig.isNull()) {
      return CodecFactory.nullCodec();
    }

    JsonNode codecConfig = compressionCodecConfig.get("codec");
    if (codecConfig == null || codecConfig.isNull() || !codecConfig.isTextual()) {
      return CodecFactory.nullCodec();
    }
    String codecType = codecConfig.asText();
    CompressionCodec codec = CompressionCodec.fromConfigValue(codecConfig.asText());
    switch (codec) {
      case NULL -> {
        return CodecFactory.nullCodec();
      }
      case DEFLATE -> {
        int compressionLevel = getCompressionLevel(compressionCodecConfig, 0, 0, 9);
        return CodecFactory.deflateCodec(compressionLevel);
      }
      case BZIP2 -> {
        return CodecFactory.bzip2Codec();
      }
      case XZ -> {
        int compressionLevel = getCompressionLevel(compressionCodecConfig, 6, 0, 9);
        return CodecFactory.xzCodec(compressionLevel);
      }
      case ZSTANDARD -> {
        int compressionLevel = getCompressionLevel(compressionCodecConfig, 3, -5, 22);
        boolean includeChecksum = getIncludeChecksum(compressionCodecConfig, false);
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

  public static int getCompressionLevel(JsonNode compressionCodecConfig, int defaultLevel, int minLevel, int maxLevel) {
    JsonNode levelConfig = compressionCodecConfig.get("compression_level");
    if (levelConfig == null || levelConfig.isNull() || !levelConfig.isIntegralNumber()) {
      return defaultLevel;
    }
    int level = levelConfig.asInt();
    if (level < minLevel || level > maxLevel) {
      throw new IllegalArgumentException(
          String.format("Invalid compression level: %d, expected an integer in range [%d, %d]", level, minLevel, maxLevel));
    }
    return level;
  }

  public static boolean getIncludeChecksum(JsonNode compressionCodecConfig, boolean defaultValue) {
    JsonNode checksumConfig = compressionCodecConfig.get("include_checksum");
    if (checksumConfig == null || checksumConfig.isNumber() || !checksumConfig.isBoolean()) {
      return defaultValue;
    }
    return checksumConfig.asBoolean();
  }

  public CodecFactory getCodecFactory() {
    return codecFactory;
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

    CompressionCodec(String configValue) {
      this.configValue = configValue;
    }

    public static CompressionCodec fromConfigValue(String configValue) {
      for (CompressionCodec codec : values()) {
        if (configValue.equalsIgnoreCase(codec.configValue)) {
          return codec;
        }
      }
      throw new IllegalArgumentException("Unknown codec config value: " + configValue);
    }

  }

}
