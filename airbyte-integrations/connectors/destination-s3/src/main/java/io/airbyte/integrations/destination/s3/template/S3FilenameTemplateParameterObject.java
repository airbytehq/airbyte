/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.template;

import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.S3Format;
import java.sql.Timestamp;
import java.util.Objects;

/**
 * This class is used as argument holder S3FilenameTemplateManager.class
 *
 * @see S3FilenameTemplateManager#applyPatternToFilename(S3FilenameTemplateParameterObject)
 */
public class S3FilenameTemplateParameterObject {

  private final String objectPath;
  private final SerializableBuffer recordsData;
  private final String fileNamePattern;
  private final String fileExtension;
  private final String partId;
  private final S3Format s3Format;
  private final Timestamp timestamp;
  private final String customSuffix;

  S3FilenameTemplateParameterObject(String objectPath,
                                    SerializableBuffer recordsData,
                                    String fileNamePattern,
                                    String fileExtension,
                                    String partId,
                                    S3Format s3Format,
                                    Timestamp timestamp,
                                    String customSuffix) {
    this.objectPath = objectPath;
    this.recordsData = recordsData;
    this.fileNamePattern = fileNamePattern;
    this.fileExtension = fileExtension;
    this.partId = partId;
    this.s3Format = s3Format;
    this.timestamp = timestamp;
    this.customSuffix = customSuffix;
  }

  public String getObjectPath() {
    return objectPath;
  }

  public SerializableBuffer getRecordsData() {
    return recordsData;
  }

  public String getFileNamePattern() {
    return fileNamePattern;
  }

  public String getFileExtension() {
    return fileExtension;
  }

  public String getPartId() {
    return partId;
  }

  public S3Format getS3Format() {
    return s3Format;
  }

  public Timestamp getTimestamp() {
    return timestamp;
  }

  public String getCustomSuffix() {
    return customSuffix;
  }

  public static S3FilenameTemplateParameterObjectBuilder builder() {
    return new S3FilenameTemplateParameterObjectBuilder();
  }

  public static class S3FilenameTemplateParameterObjectBuilder {

    private String objectPath;
    private SerializableBuffer recordsData;
    private String fileNamePattern;
    private String fileExtension;
    private String partId;
    private S3Format s3Format;
    private Timestamp timestamp;
    private String customSuffix;

    S3FilenameTemplateParameterObjectBuilder() {}

    public S3FilenameTemplateParameterObjectBuilder objectPath(String objectPath) {
      this.objectPath = objectPath;
      return this;
    }

    public S3FilenameTemplateParameterObjectBuilder recordsData(SerializableBuffer recordsData) {
      this.recordsData = recordsData;
      return this;
    }

    public S3FilenameTemplateParameterObjectBuilder fileNamePattern(String fileNamePattern) {
      this.fileNamePattern = fileNamePattern;
      return this;
    }

    public S3FilenameTemplateParameterObjectBuilder fileExtension(String fileExtension) {
      this.fileExtension = fileExtension;
      return this;
    }

    public S3FilenameTemplateParameterObjectBuilder partId(String partId) {
      this.partId = partId;
      return this;
    }

    public S3FilenameTemplateParameterObjectBuilder s3Format(S3Format s3Format) {
      this.s3Format = s3Format;
      return this;
    }

    public S3FilenameTemplateParameterObjectBuilder timestamp(Timestamp timestamp) {
      this.timestamp = timestamp;
      return this;
    }

    public S3FilenameTemplateParameterObjectBuilder customSuffix(String customSuffix) {
      this.customSuffix = customSuffix;
      return this;
    }

    public S3FilenameTemplateParameterObject build() {
      return new S3FilenameTemplateParameterObject(objectPath, recordsData, fileNamePattern, fileExtension, partId, s3Format, timestamp,
          customSuffix);
    }

    public String toString() {
      return "S3FilenameTemplateParameterObject.S3FilenameTemplateParameterObjectBuilder(objectPath=" + this.objectPath + ", recordsData="
          + this.recordsData + ", fileNamePattern="
          + this.fileNamePattern + ", fileExtension=" + this.fileExtension + ", partId=" + this.partId + ", s3Format=" + this.s3Format
          + ", timestamp=" + this.timestamp + ", customSuffix="
          + this.customSuffix + ")";
    }

  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final S3FilenameTemplateParameterObject that = (S3FilenameTemplateParameterObject) o;
    return Objects.equals(objectPath, that.objectPath) && Objects.equals(recordsData, that.recordsData)
        && Objects.equals(fileNamePattern, that.fileNamePattern)
        && Objects.equals(fileExtension, that.fileExtension) && Objects.equals(partId, that.partId) && s3Format == that.s3Format
        && Objects.equals(timestamp,
            that.timestamp)
        && Objects.equals(customSuffix, that.customSuffix);
  }

  @Override
  public int hashCode() {
    return Objects.hash(objectPath, recordsData, fileNamePattern, fileExtension, partId, s3Format, timestamp, customSuffix);
  }

}
